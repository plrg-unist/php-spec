#!/usr/bin/env python3
"""Checked-source control execution, pool lifetime, and budget resumption."""
import base64, json, re, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/semantics'))
import static_types as types

NORMAL_CASES = {
    'if-elseif': b'<?php if(false){echo "a";}elseif(false){echo "b";}elseif(true){echo "c";}else{echo "d";}echo "e";',
    'if-else': b'<?php if(0)echo "a";elseif(0)echo "b";else echo "c";',
    'if-none': b'<?php if(0)echo "a";echo "b";',
    'if-missing': b'<?php if($missing)echo "a";else echo "b";',
    'if-runtime-skip': b'<?php if(false){echo 1/0;}else{echo "b";}',
    'loop-while': b'<?php $i=0;while($i!==3){echo $i;$i=$i+1;}echo "end";',
    'loop-do': b'<?php $i=0;do{echo $i;$i=$i+1;}while($i!==3);echo "end";',
    'loop-do-once': b'<?php do{echo "once";}while(false);echo "end";',
    'loop-for': b'<?php for($i=0;$i!==3;$i=$i+1){echo $i;}echo "end";',
    'loop-for-multi': b'<?php for($i=0,$j=0;$j=$j+1,$i!==3;$i=$i+1){echo $i,":",$j,";";}echo $j;',
    'loop-empty-for': b'<?php $i=0;for(;;){$i=$i+1;if($i===3)break;echo $i;}echo "end";',
    'loop-continue': b'<?php $i=0;while($i!==3){$i=$i+1;if($i===2)continue;echo $i;}echo "end";',
    'loop-for-continue': b'<?php for($i=0;$i!==3;$i=$i+1){if($i===1)continue;echo $i;}echo "end";',
    'loop-do-continue': b'<?php $i=0;do{$i=$i+1;if($i===2)continue;echo $i;}while($i!==3);echo "end";',
    'loop-break-two': b'<?php $i=0;while($i!==3){$i=$i+1;while(true){echo $i;break 2;}echo "bad";}echo "end";',
    'loop-continue-two': b'<?php $i=0;while($i!==3){$i=$i+1;$j=0;while($j!==3){$j=$j+1;if($j===2)continue 2;echo $i,$j;}echo "bad";}echo "end";',
    'loop-for-continue-two': b'<?php for($i=0;$i!==3;$i=$i+1){do{echo $i;continue 2;}while(true);echo "bad";}echo "end";',
    'loop-condition-array': b'<?php $a=[1];while($a){echo $a[0];$a=[];}echo "end";',
    'truth-0': b'<?php if(null)echo "true";else echo "false";',
    'truth-1': b'<?php if(false)echo "true";else echo "false";',
    'truth-2': b'<?php if(true)echo "true";else echo "false";',
    'truth-3': b'<?php if(0)echo "true";else echo "false";',
    'truth-4': b'<?php if(-1)echo "true";else echo "false";',
    'truth-5': b'<?php if(0.0)echo "true";else echo "false";',
    'truth-6': b'<?php if(-0.0)echo "true";else echo "false";',
    'truth-7': b'<?php if(1.5)echo "true";else echo "false";',
    'truth-8': b'<?php if(NAN)echo "true";else echo "false";',
    'truth-9': b'<?php if(INF)echo "true";else echo "false";',
    'truth-10': b'<?php if("")echo "true";else echo "false";',
    'truth-11': b'<?php if("0")echo "true";else echo "false";',
    'truth-12': b'<?php if("00")echo "true";else echo "false";',
    'truth-13': b'<?php if([])echo "true";else echo "false";',
    'truth-14': b'<?php if([0])echo "true";else echo "false";',
    'truth-15': b'<?php if("\\x00")echo "true";else echo "false";',
    'loop-pool-reuse': b'<?php $i=0;$a=[NAN];while($i!==3){$b=[NAN];echo $a===$b;$a=$b;$i=$i+1;}',
    'loop-namespace-late-array': b'<?php namespace N;$i=0;$a=[NAN];while($i!==3){$b=[NAN];echo $a===$b;$a=$b;$i=$i+1;}',
    'loop-namespace-imported-array': b'<?php namespace N;use const NAN as X;$i=0;$a=[X];while($i!==3){$b=[X];echo $a===$b;$a=$b;$i=$i+1;}',
    'loop-string-write-cow': b'<?php $a=["abc"];$b=$a;$i=0;while($i!==3){$a[0][$i]="Z";echo $b[0],":",$a[0],";";$i=$i+1;}',
    'loop-reference-array': b'<?php $x=0;$a=[&$x];for($i=0;$i!==3;$i=$i+1){$b=$a;$b[0]=$i;echo $x;}echo $a[0];',
    'loop-namespace-warning': b'<?php namespace N;$i=0;while(NAN){echo $i;$i=$i+1;if($i===3)break;}',
}
CASES = {"control-"+name: source for name, source in NORMAL_CASES.items()}
CASES.update({
    'control-while-empty': b'<?php while(false){}',
    'control-if-empty': b'<?php if(true){}',
    'control-if-nop': b'<?php if(true);',
    'control-if-else-empty': b'<?php if(true){}else{}',
    'control-break-outside': b'<?php break\n;',
    'control-continue-outside': b'<?php continue ?>\n',
    'control-while-break-zero': b'<?php while(true){break 0;}',
    'control-while-break-negative': b'<?php while(true){break -1;}',
    'control-while-break-string': b'<?php while(true){break "2";}',
    'control-while-break-constant': b'<?php while(true){break true;}',
    'control-while-break-many': b'<?php while(true){break 2;}',
    'control-while-continue-many': b'<?php while(true){continue 2;}',
    'control-while-order': b'<?php while([&$x[]]){break 2;}',
    'control-do-order': b'<?php do{break 2;}while([&$x[]]);',
    'control-for-body-order': b'<?php for(;[&$x[]];[&$y[]]){break 2;}',
    'control-for-init-order': b'<?php for([&$z[]];[&$x[]];[&$y[]]){break 2;}',
    'control-for-step-order': b'<?php for(;[&$x[]];[&$y[]]){}',
    'control-if-branch-order': b'<?php if(false){break 2;}else{echo [&$x[]];}',
    'control-if-second-order': b'<?php if(false){}elseif([&$x[]]){break 2;}',
    'control-after-loop-depth': b'<?php while(false){} break;',
    'control-if-nan-runtime': b'<?php if(NAN){echo 1;}',
})

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
            source_path=Path(tmp)/'control.php'
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
            # Both branches retain operands until selection; dropping the unused
            # branch releases its only reference, while the selected operand lives.
            assertions.append([
                'S = $initial_state(NORMAL)[.STORE = [DEFINED (PINT 7), DEFINED (PINT 9)]][.ALLOCATIONS = [HCELL 0, HCELL 1]][.RESULT = KNOWN (PBOOL true)][.TODO = [CHOOSE ([REF_CAPTURE (REFERENCE 0) 1]) ([CHOOSE ([REF_CAPTURE (REFERENCE 1) 1]) eps 1]) 1]]',
                '$heap_valid($heap_graph(S))',
                '$prune_allocations(S).ALLOCATIONS = [HCELL 0, HCELL 1]',
                'S_selected = $choose(S[.TODO = eps], [REF_CAPTURE (REFERENCE 0) 1], [CHOOSE ([REF_CAPTURE (REFERENCE 1) 1]) eps 1], 1)',
                '$prune_allocations(S_selected).ALLOCATIONS = [HCELL 0]',
                '$heap_valid($heap_graph(S_selected))'])
            for index,checks in enumerate(assertions):
                fixture=Path(tmp)/'control.watsup'
                fixture.write_text(PREFIX+'dec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+check+'\n' for check in checks))
                run=subprocess.run([str(runner),*map(str,specs),str(fixture)],capture_output=True,text=True,cwd=ROOT,timeout=120)
                if run.returncode or run.stdout.strip()!='true':
                    (ROOT/'.tools/control-flow-failure.watsup').write_text(fixture.read_text())
                    raise AssertionError((index,run.stdout,run.stderr))
    finally:
        frontend.close();adapter.close()
    assert before==types.syntax_validation.implementation_fingerprint(),'inputs changed during control gate'
    report={'result':'pass','classification':'checked-source if/while/do/for and loop jumps; compiled pools, small-budget resumption and branch operand roots',
            'source_cases':len(records),'state_cases':len(assertions),'assertions':sum(map(len,assertions)),
            'records':records,'fingerprint':before}
    (ROOT/'coverage/semantics/control-flow.json').write_text(json.dumps(report,indent=2)+'\n')
    print({key:report[key] for key in ('result','source_cases','state_cases','assertions')})

if __name__=='__main__':
    main()
