#!/usr/bin/env python3
"""Ordered control compilation, checked metadata, and literal-depth source checks."""
import base64,copy,hashlib,json,subprocess,tempfile
from pathlib import Path
import source_compiler as compiler
from source_compiler import ROOT, types, context, occurrences

CASES = {
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
    'while-empty': b'<?php while(false){}',
    'for-empty': b'<?php for(;;);',
    'for-close-tag': b'<?php for(;;) ?>\n',
    'for-empty-comment': b'<?php for(;;)/*comment*/;',
    'for-brace-comment': b'<?php for(;;){/*comment*/}',
    'for-alt-comment': b'<?php for(;;):/*comment*/endfor;',
    'for-braced-empty': b'<?php for(;;){}',
    'for-alt-empty': b'<?php for(;;):endfor;',
    'if-empty': b'<?php if(true){}',
    'if-nop': b'<?php if(true);',
    'if-else-empty': b'<?php if(true){}else{}',
    'break-outside': b'<?php break\n;',
    'continue-outside': b'<?php continue ?>\n',
    'while-break-zero': b'<?php while(true){break 0;}',
    'while-break-negative': b'<?php while(true){break -1;}',
    'while-break-string': b'<?php while(true){break "2";}',
    'while-break-constant': b'<?php while(true){break true;}',
    'while-break-many': b'<?php while(true){break 2;}',
    'while-continue-many': b'<?php while(true){continue 2;}',
    'while-order': b'<?php while([&$x[]]){break 2;}',
    'do-order': b'<?php do{break 2;}while([&$x[]]);',
    'for-body-order': b'<?php for(;[&$x[]];[&$y[]]){break 2;}',
    'for-init-order': b'<?php for([&$z[]];[&$x[]];[&$y[]]){break 2;}',
    'for-step-order': b'<?php for(;[&$x[]];[&$y[]]){}',
    'if-branch-order': b'<?php if(false){break 2;}else{echo [&$x[]];}',
    'if-second-order': b'<?php if(false){}elseif([&$x[]]){break 2;}',
    'after-loop-depth': b'<?php while(false){} break;',
    'if-nan-runtime': b'<?php if(NAN){echo 1;}',
}

def main():
    subprocess.run([str(ROOT/'scripts/opam-exec.sh'),'dune','build','--root',str(types.HERE),'numeric_runner.exe'],cwd=ROOT,check=True,timeout=120)
    watched=[*compiler.SPECS,Path(__file__),ROOT/'tests/semantics/source_compiler.py',ROOT/'tests/semantics/_build/default/numeric_runner.exe',ROOT/'vendor/php-src/Zend/zend_compile.c']
    def fingerprint():return {'closure':types.syntax_validation.implementation_fingerprint(),'direct':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}}
    before=fingerprint()
    identity=json.loads(subprocess.run([str(types.PHP),'-n',*types.FLAGS,'-r','echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,ini_get_all(null,false)]);'],capture_output=True,text=True,env=types.ENV,timeout=10,check=True).stdout)
    assert identity[:4]==['8.5.10','cli',8,False]
    assert all(identity[4][key]==value for key,value in types.PROFILE.items())
    f=types.Worker([str(types.PHP),'-n','-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')]);a=types.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    fixtures=[];records=[];mutations=[]
    def fixture(ast,assertions):
        checked=a.request({'op':'check','ast':ast,'fixture':True});assert checked['ok'],checked
        i=len(fixtures)
        fixtures.append(f'dec $case{i}() : bool\ndef $case{i}() = true\n  -- if P = $ppstart(72, {checked["fixture"]}, {types.byte_expr(str(file))})\n'+''.join('  -- if '+test+'\n' for test in assertions))
        return checked
    try:
        with tempfile.TemporaryDirectory(dir=ROOT/'.tools') as tmp:
            file=Path(tmp)/'input.php'
            for name,source in CASES.items():
                parsed=f.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
                file.write_bytes(source);command=[str(types.PHP),'-n',*types.FLAGS,'-l',str(file)]
                run=subprocess.run(command,capture_output=True,cwd=ROOT,env=types.ENV,timeout=10)
                tests=['$pptrace(P) = '+context.expected_events(context.events(run),file),'P.LOOPS = 0']
                if run.returncode==0:tests+=['P.COMPLETION = PPCNORMAL','$access_paths(P.ACCESS) = $expression_paths(P.EXPRESSIONS)']
                checked=fixture(parsed['ast'],tests)
                records.append({'id':name,'oracle':compiler.oracle_record(source,checked,command,run),'assertions':tests})
            for source,key,values in [
                (b'<?php if(true)\n{\n}', 'statementBodyLine', [None,'-1','99','0','2','3']),
                (b'<?php for(;;)\n;','statementTerminatorLine',[None,'-1','0','99','2']),
                (b'<?php while(true){break\n;}','statementTerminatorLine',[None,'-1','0','99','2']),
            ]:
                parsed=f.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
                for value in values:
                    ast=copy.deepcopy(parsed['ast']);node=ast['program'][0]
                    if node['node']=='Stmt_While':node=node['fields'][1][0]
                    if value is None:node['meta'].pop(key)
                    else:node['meta'][key]={'int':value}
                    valid=value in (['0','2','3'] if key=='statementBodyLine' else ['2'])
                    tests=['P.LOOPS = 0']
                    if valid:
                        tests+=['P.COMPLETION = PPCNORMAL']
                        if key=='statementBodyLine':tests+=['P.LOCATION.LINE = '+('1' if value=='0' else value)]
                        elif source.startswith(b'<?php for'):tests+=['P.LOCATION.LINE = 2']
                    else:
                        reason='missing control body token line' if key=='statementBodyLine' and value is None else 'missing ordinary compiler line'
                        tests+=['P.COMPLETION = PPCABRUPT (UNSUPPORTED '+json.dumps(reason)+')']
                    checked=fixture(ast,tests)
                    mutations.append({'source_base64':base64.b64encode(source).decode(),'key':key,'value':value,'checked_ast':checked['ast'],'assertions':tests})
            # Runtime order differs from this compiler order: body-before-condition,
            # and for init/body/step/condition. Every path remains structural.
            for source,paths in [
                (b'<?php while($x){echo $y;}', [[('INDEX',0),('FIELD',1),('INDEX',0),('FIELD',0),('INDEX',0)],[('INDEX',0),('FIELD',0)]]),
                (b'<?php for($a;$b;$c){echo $d;}', [[('INDEX',0),('FIELD',0),('INDEX',0)],[('INDEX',0),('FIELD',3),('INDEX',0),('FIELD',0),('INDEX',0)],[('INDEX',0),('FIELD',2),('INDEX',0)],[('INDEX',0),('FIELD',1),('INDEX',0)]]),
            ]:
                parsed=f.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
                expected='['+', '.join(occurrences.path_term(p) for p in paths)+']'
                fixture(parsed['ast'],['P.COMPLETION = PPCNORMAL','P.LOOPS = 0','$expression_paths(P.EXPRESSIONS) = '+expected])
            script=Path(tmp)/'checks.watsup';script.write_text(compiler.PREFIX+'\n'.join(fixtures)+'dec $main() : bool\ndef $main() = true\n'+''.join(f'  -- if $case{i}()\n' for i in range(len(fixtures))))
            run=subprocess.run([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),*map(str,compiler.SPECS),str(script)],capture_output=True,text=True,timeout=120)
            if run.returncode or run.stdout.strip()!='true':
                (ROOT/'.tools/control-compiler-failure.watsup').write_text(script.read_text());raise AssertionError((run.returncode,run.stdout,run.stderr))
    finally:f.close();a.close()
    assert before==fingerprint(),'watched inputs changed'
    report={'scope':'source control compile order, literal jump legality and checked context; runtime source observations are separate','fingerprint':before,'profile':types.PROFILE,'identity':identity,'source_cases':len(records),'metadata_mutations':mutations,'path_order_checks':2,'cases':records}
    (ROOT/'coverage/semantics/control-compiler.json').write_text(json.dumps(report,indent=2)+'\n')
    print(len(records),'source compiler cases;',len(mutations),'metadata controls; 2 exact path-order checks passed')

if __name__=='__main__':main()
