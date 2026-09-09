#!/usr/bin/env python3
"""Ordinary writable fetching versus reference creation and resumed mutation."""
import base64, json, re, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/semantics'))
import static_types as types

NORMAL_CASES = {
    'original-0': b'<?php $n="a";$$n=false;$a[0][0]=1;echo $a[0][0];',
    'original-1': b'<?php $n="a";$$n=false;unset($a[0][0]);echo $a===false;',
    'original-2': b'<?php $n="a";$x=($$n=false);$x[0][0]=1;echo $x[0][0];',
    'original-3': b'<?php $a=false;$n="a";$$n=false;$a[0][0]=1;echo $a[0][0];',
    'expanded-0-0': b'<?php $n="a";$$n=false;$a[0][0]=1;echo 1;',
    'expanded-0-1': b'<?php $n="a";$$n=false;unset($a[0][0]);echo 1;',
    'expanded-0-2': b'<?php $n="a";$$n=false;$x=&$a[0];echo 1;',
    'expanded-1-0': b'<?php $a=false;$n="a";$$n=false;$a[0][0]=1;echo 1;',
    'expanded-1-1': b'<?php $a=false;$n="a";$$n=false;unset($a[0][0]);echo 1;',
    'expanded-1-2': b'<?php $a=false;$n="a";$$n=false;$x=&$a[0];echo 1;',
    'expanded-2-0': b'<?php $a=false;$r=&$a;$n="a";$$n=false;$a[0][0]=1;echo 1;',
    'expanded-2-1': b'<?php $a=false;$r=&$a;$n="a";$$n=false;unset($a[0][0]);echo 1;',
    'expanded-2-2': b'<?php $a=false;$r=&$a;$n="a";$$n=false;$x=&$a[0];echo 1;',
    'expanded-3-0': b'<?php $a=false;$r=&$a;unset($r);$n="a";$$n=false;$a[0][0]=1;echo 1;',
    'expanded-3-1': b'<?php $a=false;$r=&$a;unset($r);$n="a";$$n=false;unset($a[0][0]);echo 1;',
    'expanded-3-2': b'<?php $a=false;$r=&$a;unset($r);$n="a";$$n=false;$x=&$a[0];echo 1;',
    'expanded-4-0': b'<?php $a=false;$n="a";$v=($$n=false);$a[0][0]=1;echo 1;',
    'expanded-4-1': b'<?php $a=false;$n="a";$v=($$n=false);unset($a[0][0]);echo 1;',
    'expanded-4-2': b'<?php $a=false;$n="a";$v=($$n=false);$x=&$a[0];echo 1;',
    'expanded-5-0': b'<?php $n="a";$$n=[false];$b=$a;$a[0][0]=1;echo 1;',
    'expanded-5-1': b'<?php $n="a";$$n=[false];$b=$a;unset($a[0][0]);echo 1;',
    'expanded-5-2': b'<?php $n="a";$$n=[false];$b=$a;$x=&$a[0];echo 1;',
    'expanded-6-0': b'<?php $a=[false];$n="a";$$n[0]=false;$a[0][0]=1;echo 1;',
    'expanded-6-1': b'<?php $a=[false];$n="a";$$n[0]=false;unset($a[0][0]);echo 1;',
    'expanded-6-2': b'<?php $a=[false];$n="a";$$n[0]=false;$x=&$a[0];echo 1;',
    'expanded-7-0': b'<?php $a=[false];$r=&$a[0];unset($r);$n="a";$$n[0]=false;$a[0][0]=1;echo 1;',
    'expanded-7-1': b'<?php $a=[false];$r=&$a[0];unset($r);$n="a";$$n[0]=false;unset($a[0][0]);echo 1;',
    'expanded-7-2': b'<?php $a=[false];$r=&$a[0];unset($r);$n="a";$$n[0]=false;$x=&$a[0];echo 1;',
    'loop-plain-write': b'<?php $n="a";$i=0;while($i<3){$$n=false;$a[0][0]=$i;echo $a[0][0];$i=$i+1;}',
    'loop-singleton-write': b'<?php $a=false;$r=&$a;unset($r);$n="a";$i=0;while($i<3){$$n=false;$a[0][0]=$i;echo $a[0][0];$i=$i+1;}',
}
CASES = {"write-fetch-"+name: source for name,source in NORMAL_CASES.items()}

STATE_CHECKS = ['S = $fetch_write_name($initial_state(NORMAL), [97])', 'S.STORE = [DEFINED PNULL]', 'S.REFCELLS = eps', 'S_ref = $acquire_name($initial_state(NORMAL), [97])', 'S_ref = S[.REFCELLS = [0]]', '$heap_graph(S_ref) = $heap_graph(S)', '$fetch_write_name(S_ref, [97]) = S_ref', 'S_alias = $bind_reference(S_ref, [114])', 'S_single = $unset_name($release_temporaries(S_alias), [114])', '$fetch_write_name(S_single, [97]) = S_single', 'S_new = $fetch_write_name(S_single, [98])', 'S_new.REFCELLS = [0]', 'S_new.CELL = 1', 'S_written = $write_name(S_new, [98], PBOOL false)', 'S_written.REFCELLS = [0]']

PREFIX = '''
var U : pcunit
dec $outputs(pevent*) : nat*
def $outputs(eps) = eps
def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)
def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)
def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)
dec $messages(pevent*) : pevent*
def $messages(eps) = eps
def $messages((OUTPUT n*) :: pevent*) = $messages(pevent*)
def $messages((WARNING n* z) :: pevent*) = (WARNING n* z) :: $messages(pevent*)
def $messages((DIAGNOSTIC text n* z) :: pevent*) = (DIAGNOSTIC text n* z) :: $messages(pevent*)
'''

def byte_sequence(value):
    return '(['+','.join(map(str,value))+'])'

def main():
    subprocess.run([str(ROOT/'scripts/opam-exec.sh'),'dune','build','--root',str(ROOT/'tests/semantics'),'numeric_runner.exe'],cwd=ROOT,check=True,timeout=120)
    runner=ROOT/'tests/semantics/_build/default/numeric_runner.exe'
    specs=[ROOT/p for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
    before=types.syntax_validation.implementation_fingerprint()
    frontend=types.Worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')])
    adapter=types.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    records=[]; assertions=[]
    try:
        with tempfile.TemporaryDirectory(dir=ROOT/'.tools') as tmp:
            source_path=Path(tmp)/'write-fetch.php'
            for name,source in NORMAL_CASES.items():
                source_path.write_bytes(source)
                native=subprocess.run([str(types.PHP),'-n',*types.FLAGS,str(source_path)],capture_output=True,env=types.ENV,timeout=10)
                assert native.returncode==0,(name,native.stdout,native.stderr)
                parsed=frontend.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
                checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True});assert checked['ok'],checked
                events=[]
                for severity,message,line in re.findall(rb'(Warning|Deprecated): (.*?) in .*? on line (\d+)',native.stderr):
                    if message.startswith(b'Undefined variable $'):
                        events.append('WARNING '+byte_sequence(message.removeprefix(b'Undefined variable $'))+' '+line.decode())
                    else:
                        events.append('DIAGNOSTIC "'+severity.decode()+'" '+byte_sequence(message)+' '+line.decode())
                checks=['U = $pcsource(0, '+checked['fixture']+')',
                        'S_initial = $php_run('+checked['fixture']+', 0, '+json.dumps(base64.b64encode(str(source_path).encode()).decode())+')',
                        'S_initial.COMPLETION = BUDGET','S = S_initial[.COMPLETION = NORMAL]',
                        'S.SOURCES = [U]','S_out = $drive(S, 10000)',
                        '$outputs(S_out.EVENTS) = '+byte_sequence(native.stdout),
                        '$messages(S_out.EVENTS) = ['+', '.join(events)+']',
                        'S_out.COMPLETION = NORMAL','S_out.ORIGIN = eps','S_out.HELD = eps',
                        'S_out.POOLS = S.POOLS','S_out.CODE = S.CODE',
                        '$heap_valid($heap_graph(S_out))']
                if name.startswith('loop-'):
                    for budget in (1,2,5,9,17,31,63):
                        checks += [f'S_budget{budget} = $drive(S, {budget})',
                                   f'$drive(S_budget{budget}[.COMPLETION = NORMAL], 10000) = S_out',
                                   f'S_budget{budget}.POOLS = S.POOLS',
                                   f'S_budget{budget}.CODE = S.CODE',
                                   f'$heap_valid($heap_graph(S_budget{budget}))']
                assertions.append(checks)
                records.append({'id':name,'source_base64':base64.b64encode(source).decode(),'ast':checked['ast'],
                                'oracle_stdout':base64.b64encode(native.stdout).decode(),
                                'oracle_stderr':base64.b64encode(native.stderr).decode()})
            parsed=frontend.request({'op':'parse','source':base64.b64encode(b'<?php;').decode()});assert parsed['accepted'],parsed
            checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True});assert checked['ok'],checked
            assertions.append(STATE_CHECKS)
            for index,checks in enumerate(assertions):
                fixture=Path(tmp)/'write-fetch.watsup'
                fixture.write_text(PREFIX+'dec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+check+'\n' for check in checks))
                run=subprocess.run([str(runner),*map(str,specs),str(fixture)],capture_output=True,text=True,cwd=ROOT,timeout=120)
                if run.returncode or run.stdout.strip()!='true':
                    (ROOT/'.tools/write-fetch-failure.watsup').write_text(fixture.read_text())
                    raise AssertionError((index,run.stdout,run.stderr))
    finally:
        frontend.close();adapter.close()
    assert before==types.syntax_validation.implementation_fingerprint(),'inputs changed during writable-fetch gate'
    report={'result':'pass','classification':'checked-source ordinary writable fetching versus reference creation; retained regression originals, marker preservation and resumption',
            'source_cases':len(records),'state_cases':len(assertions),'assertions':sum(map(len,assertions)),
            'records':records,'fingerprint':before}
    (ROOT/'coverage/semantics/write-fetch.json').write_text(json.dumps(report,indent=2)+'\n')
    print({key:report[key] for key in ('result','source_cases','state_cases','assertions')})

if __name__=='__main__':
    main()
