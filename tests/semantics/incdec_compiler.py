#!/usr/bin/env python3
"""Original inc/dec compiler barriers, rejection order and effective access lines."""
import base64,copy,hashlib,json,subprocess,tempfile
from pathlib import Path
import source_compiler as compiler
from source_compiler import ROOT,types,context,occurrences

CASES={
    'pre++$x': b'<?php use A; ++$x; use B;',
    'pre++$a[]': b'<?php use A; ++$a[]; use B;',
    'pre++$a[0][]': b'<?php use A; ++$a[0][]; use B;',
    'pre++${"name"}': b'<?php use A; ++${"name"}; use B;',
    'pre++$a[NAN == true]': b'<?php use A; ++$a[NAN == true]; use B;',
    'post++$x': b'<?php use A; $x++; use B;',
    'post++$a[]': b'<?php use A; $a[]++; use B;',
    'post++$a[0][]': b'<?php use A; $a[0][]++; use B;',
    'post++${"name"}': b'<?php use A; ${"name"}++; use B;',
    'post++$a[NAN == true]': b'<?php use A; $a[NAN == true]++; use B;',
    'pre--$x': b'<?php use A; --$x; use B;',
    'pre--$a[]': b'<?php use A; --$a[]; use B;',
    'pre--$a[0][]': b'<?php use A; --$a[0][]; use B;',
    'pre--${"name"}': b'<?php use A; --${"name"}; use B;',
    'pre--$a[NAN == true]': b'<?php use A; --$a[NAN == true]; use B;',
    'post--$x': b'<?php use A; $x--; use B;',
    'post--$a[]': b'<?php use A; $a[]--; use B;',
    'post--$a[0][]': b'<?php use A; $a[0][]--; use B;',
    'post--${"name"}': b'<?php use A; ${"name"}--; use B;',
    'post--$a[NAN == true]': b'<?php use A; $a[NAN == true]--; use B;',
    'inc-after-failure': b'<?php [&$x[]]; ++$a[NAN == true];',
    'inc-before-failure': b'<?php ++$a[NAN == true]; [&$x[]];',
    'inc-nested-failure': b'<?php ++$a[[&$x[]]];',
    'inc-lines': b'<?php ++\n$a[\nNAN == true\n];',
    'inc-name-lines': b'<?php ++\n${\n"x"\n};',
    'header-rw': b'<?php $http_response_header++;',
    'header-write': b'<?php $http_response_header=1;',
    'this-rw': b'<?php $this++;',
    'globals-rw': b'<?php $GLOBALS++;',
    'function-rw': b'<?php foo()++;',
    'method-rw': b'<?php $x->foo()++;',
    'string-offset': b'<?php $x="1"; $x[0]++;',
    'reject-target-0': b'<?php\nfoo([&$q[]])++;',
    'reject-target-1': b'<?php\n$x->foo([&$q[]])++;',
    'reject-target-2': b'<?php\n$x?->foo([&$q[]])++;',
    'reject-target-3': b'<?php\nA::foo([&$q[]])++;',
    'reject-target-4': b'<?php\n$x?->p++;',
    'reject-target-5': b'<?php\n$x?->p[0]++;',
    'reject-target-6': b'<?php\n$x?->p->q++;',
    'reject-target-7': b'<?php\n(\n$f\n)()++;',
    'reject-target-8': b'<?php\n(\n$x\n)->foo()++;',
    'array-value-++$a': b'<?php $a=1;$b=[++$a];',
    'array-key-++$a': b'<?php $a=1;$b=[++$a=>1];',
    'logical-skipped-++$a': b'<?php $a=1;false && [++$a];',
    'ternary-skipped-++$a': b'<?php $a=1;$b=[true?1:++$a];',
    'ordinary-visited-++$a': b'<?php $a=1;$b=[false?1:++$a];',
    'array-value-$a++': b'<?php $a=1;$b=[$a++];',
    'array-key-$a++': b'<?php $a=1;$b=[$a++=>1];',
    'logical-skipped-$a++': b'<?php $a=1;false && [$a++];',
    'ternary-skipped-$a++': b'<?php $a=1;$b=[true?1:$a++];',
    'ordinary-visited-$a++': b'<?php $a=1;$b=[false?1:$a++];',
    'array-value---$a': b'<?php $a=1;$b=[--$a];',
    'array-key---$a': b'<?php $a=1;$b=[--$a=>1];',
    'logical-skipped---$a': b'<?php $a=1;false && [--$a];',
    'ternary-skipped---$a': b'<?php $a=1;$b=[true?1:--$a];',
    'ordinary-visited---$a': b'<?php $a=1;$b=[false?1:--$a];',
    'array-value-$a--': b'<?php $a=1;$b=[$a--];',
    'array-key-$a--': b'<?php $a=1;$b=[$a--=>1];',
    'logical-skipped-$a--': b'<?php $a=1;false && [$a--];',
    'ternary-skipped-$a--': b'<?php $a=1;$b=[true?1:$a--];',
    'ordinary-visited-$a--': b'<?php $a=1;$b=[false?1:$a--];',
    'prepass-order-0': b'<?php use A;$b=[++$a[[&$q[]]]];use B;',
    'prepass-order-1': b'<?php use A;$b=[foo([&$q[]])++];use B;',
    'prepass-order-2': b'<?php use A;$b=[true?1:foo([&$q[]])++];use B;',
    'prepass-order-3': b'<?php use A;$b=[false && foo([&$q[]])++];use B;',
    'prepass-order-4': b'<?php use A;$b=[++$a[NAN == true], [&$q[]]];use B;',
    'prepass-order-5': b'<?php use A;$b=[++$a[[&$q[]]], NAN == true];use B;',
    'deep-barrier-skipped': b'<?php echo [false && ++$a[[[]=>1]]][0];',
    'deep-barrier-visited': b'<?php echo [true && ++$a[[[]=>1]]][0];',
    'retained-array-value': b'<?php $a=1;$b=[$a++];echo $b[0],$a;',
    'retained-array-key': b'<?php $a=1;$b=[$a++=>9];echo $b[1],$a;',
    'retained-skipped-control': b'<?php $a=1;echo [true ? 7 : $a++][0],$a;',
    'callable-line-0': b'<?php\n(\n$f\n)()++;',
    'callable-line-1': b'<?php\n(\n$f)\n()++;',
    'callable-line-2': b'<?php\n$f\n(\n[&$q[]]\n)++;',
    'callable-line-3': b'<?php\nfoo\n(\n[&$q[]]\n)++;',
    'callable-line-4': b'<?php\n$f\n(\n1\n)++;',
    'callable-line-5': b'<?php\n$f(\n\n1\n)++;',
    'callable-line-6': b'<?php\n$f\n( \n1\n)++;',
    'callable-line-7': b'<?php\n$f (\n\n1\n)++;',
}
CASES.update({
    'this-literal-0': b'<?php use A;$this=1;use B;',
    'this-literal-1': b'<?php use A;$this=&$x;use B;',
    'this-literal-2': b'<?php use A;unset($this);use B;',
    'this-literal-3': b'<?php use A;$a=&$this;use B;',
    'this-literal-4': b'<?php use A;$this[0]=1;use B;',
    'this-literal-5': b'<?php use A;unset($this[0]);use B;',
    'this-literal-6': b'<?php use A;$this=[&$a[]];use B;',
    'this-literal-7': b'<?php use A;$this=&$a[];use B;',
    'this-literal-8': b'<?php use A;false && ($this=1);use B;',
    'this-literal-9': b'<?php use A;[true?1:($this=1)];use B;',
    'this-literal-10': b'<?php use A;[false && ($this=1)];use B;',
    'this-literal-11': b'<?php use A;unset($x[],$this);use B;',
    'this-literal-12': b'<?php use A;unset($x[\n0\n],\n$this);use B;',
    'this-literal-13': b'<?php use A;\n$this\n=\n1;use B;',
    'this-string-0': b'<?php use A;${"this"}=1;use B;',
    'this-string-1': b'<?php use A;${"this"}=&$x;use B;',
    'this-string-2': b'<?php use A;unset(${"this"});use B;',
    'this-string-3': b'<?php use A;$a=&${"this"};use B;',
    'this-string-4': b'<?php use A;${"this"}[0]=1;use B;',
    'this-string-5': b'<?php use A;unset(${"this"}[0]);use B;',
    'this-string-6': b'<?php use A;${"this"}=[&$a[]];use B;',
    'this-string-7': b'<?php use A;${"this"}=&$a[];use B;',
    'this-string-8': b'<?php use A;false && (${"this"}=1);use B;',
    'this-string-9': b'<?php use A;[true?1:(${"this"}=1)];use B;',
    'this-string-10': b'<?php use A;[false && (${"this"}=1)];use B;',
    'this-string-11': b'<?php use A;unset($x[],${"this"});use B;',
    'this-string-12': b'<?php use A;unset($x[\n0\n],\n${"this"});use B;',
    'this-string-13': b'<?php use A;\n${"this"}\n=\n1;use B;',
})
LINES=[b'<?php $a=true;\necho ++\n$a;', b'<?php $a=true;\necho --\n$a;', b'<?php $a=true;\necho $a\n++;', b'<?php $a=true;\necho $a\n--;', b'<?php $a=[];\necho ++$a[\n0\n];', b'<?php $a=[];\necho --$a[\n0\n];', b'<?php $a=[];\necho $a[\n0\n]++;', b'<?php $a=[];\necho $a[\n0\n]--;']


def fingerprint():
    watched=[*compiler.SPECS,Path(__file__),ROOT/'tests/semantics/source_compiler.py',ROOT/'tests/semantics/_build/default/numeric_runner.exe',ROOT/'vendor/php-src/Zend/zend_compile.c']
    return {'closure':types.syntax_validation.implementation_fingerprint(),'direct':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}}


def main():
    subprocess.run([str(ROOT/'scripts/opam-exec.sh'),'dune','build','--root',str(types.HERE),'numeric_runner.exe'],cwd=ROOT,check=True,timeout=120)
    before=fingerprint()
    identity=json.loads(subprocess.run([str(types.PHP),'-n',*types.FLAGS,'-r','echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,ini_get_all(null,false)]);'],capture_output=True,text=True,env=types.ENV,timeout=10,check=True).stdout)
    assert identity[:4]==['8.5.10','cli',8,False]
    assert all(identity[4][k]==v for k,v in types.PROFILE.items())
    I=compiler.I;F=compiler.F
    access_cases=compiler.ACCESS_CASES+[(b'<?php ++$a[0];',[([I(0),F(0)],'PPR'),([I(0),F(0),F(0)],'PPRW'),([I(0),F(0),F(0),F(0)],'PPRW'),([I(0),F(0),F(0),F(1)],'PPR')]),(b'<?php $a[0][]++;',[([I(0),F(0),F(0)],'PPRW'),([I(0),F(0),F(0),F(0)],'PPRW'),([I(0),F(0),F(0),F(0),F(0)],'PPRW'),([I(0),F(0),F(0),F(0),F(1)],'PPR')])]
    f=types.Worker([str(types.PHP),'-n','-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')]);a=types.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    fixtures=[];records=[];roles=[];emissions=[];metadata_checks=[]
    def fixture(ast,checks):
        checked=a.request({'op':'check','ast':ast,'fixture':True});assert checked['ok'],checked
        i=len(fixtures);fixtures.append(f'dec $case{i}() : bool\ndef $case{i}() = true\n  -- if P = $ppstart(74, {checked["fixture"]}, {types.byte_expr(str(file))})\n'+''.join('  -- if '+test+'\n' for test in checks));return checked
    try:
        with tempfile.TemporaryDirectory(dir=ROOT/'.tools') as tmp:
            file=Path(tmp)/'input.php'
            for name,source in CASES.items():
                parsed=f.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
                file.write_bytes(source);command=[str(types.PHP),'-n',*types.FLAGS,'-l',str(file)];run=subprocess.run(command,capture_output=True,cwd=ROOT,env=types.ENV,timeout=10)
                checks=['$pptrace(P) = '+context.expected_events(context.events(run),file),'P.FOLD.WARNINGS = eps']
                if run.returncode==0:checks+=['P.COMPLETION = PPCNORMAL','$access_paths(P.ACCESS) = $expression_paths(P.EXPRESSIONS)']
                checked=fixture(parsed['ast'],checks);records.append({'id':name,'oracle':compiler.oracle_record(source,checked,command,run),'assertions':checks})
            for source,probes in access_cases:
                parsed=f.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
                checks=['P.COMPLETION = PPCNORMAL','$access_paths(P.ACCESS) = $expression_paths(P.EXPRESSIONS)']
                checks += [f'$ppaccess(P, {occurrences.path_term(path)}) = '+('eps' if mode is None else '('+mode+')') for path,mode in probes]
                fixture(parsed['ast'],checks);roles.append({'source_base64':base64.b64encode(source).decode(),'assertions':checks})
            for source in LINES:
                parsed=f.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
                file.write_bytes(source);command=[str(types.PHP),'-n',*types.FLAGS,str(file)];run=subprocess.run(command,capture_output=True,cwd=ROOT,env=types.ENV,timeout=10)
                assert run.returncode==0,(source,run.stderr)
                events=context.events(run);assert events,source
                line=events[-1][2];path=occurrences.path_term([I(1),F(0),I(0)])
                checks=['P.COMPLETION = PPCNORMAL',f'$pprecord(P.EXPRESSIONS, {path}) = (PPCEXPR {path} {line} pvalue?)']
                checked=fixture(parsed['ast'],checks);emissions.append({'oracle':compiler.oracle_record(source,checked,command,run),'assertions':checks})
            source=b'<?php $f()++;'
            parsed=f.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
            for value in [None,'0','-1','17']:
                edited=copy.deepcopy(parsed['ast']);target=edited['program'][0]['fields'][0]['fields'][0]
                if value is None:target['meta'].pop('callableExprLine')
                else:target['meta']['callableExprLine']={'int':value}
                checks=['P.COMPLETION = PPCABRUPT (UNSUPPORTED "missing ordinary compiler line")'] if value!='17' else ['P.COMPLETION = PPCABRUPT (STATICERROR "Can\'t use function return value in write context" 17)']
                fixture(edited,checks);metadata_checks.append({'value':value,'assertions':checks})
            for source in [b'<?php unset($this);', b'<?php $this=1;']:
                parsed=f.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
                for value in [None,'0','-1','17']:
                    edited=copy.deepcopy(parsed['ast']);statement=edited['program'][0]
                    target=statement['fields'][0][0] if statement['node']=='Stmt_Unset' else statement['fields'][0]['fields'][0]
                    if value is None:target['meta'].pop('startLine')
                    else:target['meta']['startLine']={'int':value}
                    message='Cannot unset $this' if statement['node']=='Stmt_Unset' else 'Cannot re-assign $this'
                    checks=['P.COMPLETION = PPCABRUPT (UNSUPPORTED "missing ordinary compiler line")'] if value!='17' else [f'P.COMPLETION = PPCABRUPT (STATICERROR "{message}" 17)']
                    fixture(edited,checks);metadata_checks.append({'source_base64':base64.b64encode(source).decode(),'value':value,'assertions':checks})
            script=Path(tmp)/'checks.watsup';script.write_text(compiler.PREFIX+'\ndec $pprecord(ppexprdone*, pcpath) : ppexprdone?\ndef $pprecord(eps, pcpath) = eps\ndef $pprecord((PPCEFFECT pcpath_effect) :: ppexprdone*, pcpath) = $pprecord(ppexprdone*, pcpath)\ndef $pprecord((PPCEXPR pcpath n pvalue?) :: ppexprdone*, pcpath) = (PPCEXPR pcpath n pvalue?)\ndef $pprecord((PPCEXPR pcpath_other n pvalue?) :: ppexprdone*, pcpath) = $pprecord(ppexprdone*, pcpath)\n  -- if pcpath_other =/= pcpath\n'+'\n'.join(fixtures)+'dec $main() : bool\ndef $main() = true\n'+''.join(f'  -- if $case{i}()\n' for i in range(len(fixtures))))
            run=subprocess.run([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),*map(str,compiler.SPECS),str(script)],capture_output=True,text=True,timeout=120)
            if run.returncode or run.stdout.strip()!='true':
                (ROOT/'.tools/incdec-compiler-failure.watsup').write_text(script.read_text());raise AssertionError((run.returncode,run.stdout,run.stderr))
    finally:f.close();a.close()
    assert before==fingerprint(),'watched inputs changed'
    report={'scope':'original inc/dec prepass barriers, static rejection order, access and effective lines; runtime evidence separate','fingerprint':before,'profile':types.PROFILE,'oracle_identity':identity,'source_cases':len(records),'access_sources':len(roles),'access_paths':sum(len(probes) for _,probes in access_cases),'roles':roles,'cases':records,'emission_lines':emissions,'metadata_checks':metadata_checks}
    (ROOT/'coverage/semantics/incdec-compiler.json').write_text(json.dumps(report,indent=2)+'\n');print(len(records),'native lint comparisons;',len(roles),'access sources;',report['access_paths'],'access paths;',len(emissions),'emission observations;',len(metadata_checks),'source context boundaries passed')

if __name__=='__main__':main()
