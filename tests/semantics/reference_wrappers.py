#!/usr/bin/env python3
"""Reference-wrapper history, FETCH diagnostics and owner/pool invariants."""
import base64, json, re, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/semantics'))
import static_types as types

NORMAL_CASES = {
    'nested-reference': b'<?php $a=false;$r=&$a;$a[0][0]=1;echo $a[0][0];',
    'nested-singleton-reference': b'<?php $a=false;$r=&$a;unset($r);$a[0][0]=1;echo $a[0][0];',
    'nested-plain-control': b'<?php $a=false;$a[0][0]=1;echo $a[0][0];',
    'reference-fetch': b'<?php $a=false;$r=&$a;$x=&$a[0];echo $x===null;',
    'final-reference': b'<?php $a=false;$r=&$a;$a[0]=1;echo $a[0];',
    'final-singleton-reference': b'<?php $a=false;$r=&$a;unset($r);$a[0]=1;echo $a[0];',
    'final-plain': b'<?php $a=false;$a[0]=1;echo $a[0];',
    'write-through-history': b'<?php $a=false;$r=&$a;$a=false;$a[0][0]=1;echo $a[0][0];',
    'fresh-binding-after-unset': b'<?php $a=false;$r=&$a;unset($a);$a=false;$a[0][0]=1;echo $a[0][0];',
    'cow-singleton-unwrapping': b'<?php $x=false;$a=[&$x];unset($x);$b=$a;$b[0][0][0]=1;$a[0][0][0]=2;echo $a[0][0][0],$b[0][0][0];',
    'cow-shared-reference': b'<?php $x=false;$a=[&$x];$b=$a;$b[0][0][0]=1;echo $a[0][0][0],$b[0][0][0];',
    'value-copy-is-plain': b'<?php $a=false;$r=&$a;$b=$a;$b[0][0]=1;echo $b[0][0];',
    'dead-cycle-reference': b'<?php $a=false;$r=&$a;$cycle=[&$r];$cycle[1]=&$cycle;unset($r,$cycle);$a[0][0]=1;echo $a[0][0];',
    'element-singleton-reference': b'<?php $x=false;$a=[&$x];unset($x);$a[0][0][0]=1;echo $a[0][0][0];',
    'alias-chain-history': b'<?php $a=false;$x=&$a;$y=&$x;$x=2;unset($x,$y);$a=false;$a[0][0]=1;echo $a[0][0];',
    'loop-wrapper-history': b'<?php $a=false;$r=&$a;unset($r);$i=0;while($i<3){$a=false;$a[0][0]=$i;echo $a[0][0];$i=$i+1;}',
    'loop-wrapper-cow': b'<?php $x=false;$a=[&$x];for($i=0;$i<3;$i=$i+1){$x=false;$b=$a;$b[0][0][0]=$i;echo $a[0][0][0];}',
    'nested-unset-reference': b'<?php $a=false;$r=&$a;unset($a[0][0]);echo $a===false;',
    'nested-unset-singleton': b'<?php $a=false;$r=&$a;unset($r);unset($a[0][0]);echo $a===false;',
    'nested-unset-plain': b'<?php $a=false;unset($a[0][0]);echo $a===false;',
    'final-unset-reference': b'<?php $a=false;$r=&$a;unset($a[0]);echo $a===false;',
}
CASES = {"reference-wrapper-"+name: source for name,source in NORMAL_CASES.items()}

STATE_CHECKS = [
    'S = $write_name($initial_state(NORMAL), [97], PBOOL false)',
    'S.REFCELLS = eps',
    '$location_reference(S, ROOT 0) = false',
    'S_ref = $acquire_name(S, [97])',
    'S_ref.REFCELLS = [0]',
    '$reference_cell(S_ref, 0) = S_ref',
    '$location_reference(S_ref, ROOT 0)',
    'S_alias = $bind_reference(S_ref, [114])',
    'S_single = $unset_name($release_temporaries(S_alias), [114])',
    'S_single.REFCELLS = [0]',
    '$heap_owners($heap_graph(S_single), HCELL 0) = 1',
    '$heap_graph(S_single) = $heap_graph(S)',
    '$fetch_location_array(S_single, ROOT 0, 1).EVENTS = eps',
    '|$location_array(S_single, ROOT 0, 1).EVENTS| = 1',
    '|$fetch_location_array(S, ROOT 0, 1).EVENTS| = 1',
    'S_dead = $unset_name(S_single, [97])',
    '$heap_prune($heap_graph(S_dead)).NODES = eps',
    '$prune_allocations(S_dead).REFCELLS = [0]',
    'S_new = $write_name($prune_allocations(S_dead), [97], PBOOL false)',
    '$lookup(S_new.ENV, [97]) = (1)',
    '$location_reference(S_new, ROOT 1) = false',
    'S_cycle = $initial_state(NORMAL)[.STORE = [DEFINED (PARRAY 0)]][.REFCELLS = [0]][.ARRAYS = [{ITEMS ([ENTRY (KINT 0) (ALIAS 0)]), NEXT 1}]][.ALLOCATIONS = [HCELL 0, HARRAY 0]]',
    '$heap_valid($heap_graph(S_cycle))',
    '$heap_prune($heap_graph(S_cycle)).NODES = [HCELL 0, HARRAY 0]',
    '$heap_collect($heap_graph(S_cycle)).NODES = eps',
    '$heap_graph(S_cycle) = $heap_graph(S_cycle[.REFCELLS = eps])',
    'P.COMPLETION = PPCNORMAL',
    '$compile_source(S_ref, P).REFCELLS = [0]',
    'P_bad = P[.FOLD = P.FOLD[.MEMORY = P.FOLD.MEMORY[.REFCELLS = [0]]]]',
    '$compile_source(S_ref, P_bad).COMPLETION = UNSUPPORTED "compiler variable storage in constant pool"',
    '$compile_source(S_ref, P_bad).POOLS = eps',
]

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
            source_path=Path(tmp)/'reference-wrappers.php'
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
            assertions.append(['P = $ppstart(0, '+checked['fixture']+', [47,97])']+STATE_CHECKS)
            for index,checks in enumerate(assertions):
                fixture=Path(tmp)/'reference-wrappers.watsup'
                fixture.write_text(PREFIX+'dec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+check+'\n' for check in checks))
                run=subprocess.run([str(runner),*map(str,specs),str(fixture)],capture_output=True,text=True,cwd=ROOT,timeout=120)
                if run.returncode or run.stdout.strip()!='true':
                    (ROOT/'.tools/reference-wrappers-failure.watsup').write_text(fixture.read_text())
                    raise AssertionError((index,run.stdout,run.stderr))
    finally:
        frontend.close();adapter.close()
    assert before==types.syntax_validation.implementation_fingerprint(),'inputs changed during wrapper gate'
    report={'result':'pass','classification':'checked-source wrapper history and FETCH versus final mutation diagnostics; owner, cycle collection graph and constant pool boundaries',
            'source_cases':len(records),'state_cases':len(assertions),'assertions':sum(map(len,assertions)),
            'records':records,'fingerprint':before}
    (ROOT/'coverage/semantics/reference-wrappers.json').write_text(json.dumps(report,indent=2)+'\n')
    print({key:report[key] for key in ('result','source_cases','state_cases','assertions')})

if __name__=='__main__':
    main()
