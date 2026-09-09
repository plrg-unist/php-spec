#!/usr/bin/env python3
"""Magic constants: native phases, ordinary operands, prepass facts and context."""
import base64,copy,hashlib,json,subprocess,tempfile
from pathlib import Path
import source_compiler as compiler
from source_compiler import types,context
from magic_constants import CASES
ROOT=Path(__file__).resolve().parents[2]
REPORT=ROOT/'coverage/semantics/magic-constants-compiler.json'
NAME_CHECKS={
 'magic-autoglobal-name':['P.AUTOGLOBALS = [[95,69,78,86]]','P.CVS = eps'],
 'magic-concat-globals-name':['P.AUTOGLOBALS = [[71,76,79,66,65,76,83]]','P.CVS = eps'],
 'magic-header-name':['P.HEADERASSIGNED = false','P.CVS = eps'],
 'magic-header-after-cv':['P.HEADERASSIGNED = true'],
 'literal-global-priority':['P.FOLD.FACTS = eps'],
 'computed-global-priority':['P.COMPLETION = PPCNORMAL'],
}
CASES = {**CASES, 'function-body-magic': b'<?php function f(){echo __FUNCTION__;}'}
NAME_CHECKS['function-body-magic'] = ['P.COMPLETION = PPCNORMAL', 'P.FUNCTIONS = [pfunction]', 'pfunction.NAME = [102]', 'P.FOLD.FUNCTION = eps']
DECLARATIONS={
 'class':b'<?php class C { const X=__CLASS__; }',
 'trait':b'<?php trait T { const X=__TRAIT__; }',
 'closure':b'<?php $f=function(){echo __FUNCTION__;};',
}

def inputs():
    paths=[*compiler.SPECS,Path(__file__),Path(__file__).with_name('magic_constants.py'),
           ROOT/'frontend/worker.php',ROOT/'spec/schema.json',types.PHP,ROOT/'.tools/php-file.so',
           ROOT/'_build/default/adapter/main.exe',ROOT/'tests/semantics/_build/default/numeric_runner.exe']
    return {'closure':types.syntax_validation.implementation_fingerprint(),
            'direct':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}

def magic_node(ast):
    todo=[ast]
    while todo:
        node=todo.pop()
        if isinstance(node,dict):
            if node.get('node','').startswith('Scalar_MagicConst_'):return node
            todo.extend(node.values())
        elif isinstance(node,list):todo.extend(node)
    raise AssertionError('missing magic node')

def main():
    before=inputs();fixtures=[];records=[];boundaries=[]
    frontend=types.Worker([str(types.PHP),'-n','-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')])
    adapter=types.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    def parse(source):
        result=frontend.request({'op':'parse','source':base64.b64encode(source).decode()})
        assert result['accepted'],result
        return result['ast']
    def add(name,ast,path,checks,cwd=None):
        checked=adapter.request({'op':'check','ast':ast,'fixture':True});assert checked['ok'],checked
        call='$ppstart(91, '+checked['fixture']+', '+types.byte_expr(str(path))+')'
        if cwd is not None:call='$ppstart_cwd(91, '+checked['fixture']+', '+types.byte_expr(str(path))+', '+cwd+')'
        n=len(fixtures)
        fixtures.append(f'dec $case{n}() : bool\ndef $case{n}() = true\n  -- if P = '+call+'\n'+''.join('  -- if '+check+'\n' for check in checks))
        boundaries.append({'id':name,'checks':checks,'cwd':cwd})
    try:
        with tempfile.TemporaryDirectory(prefix='php-magic-compiler-',dir=ROOT/'.tools') as directory:
            work=Path(directory).resolve()
            for i,(name,source) in enumerate(CASES.items()):
                path=work/f'source-{i}.php';path.write_bytes(source);ast=parse(source)
                native=subprocess.run([str(types.PHP),'-n',*types.FLAGS,'-l',str(path)],capture_output=True,env=types.ENV,timeout=10)
                expected=context.expected_events(context.events(native),path)
                checks=['$pptrace(P) = '+expected,*NAME_CHECKS.get(name,[])]
                row={'id':name,'source_sha256':hashlib.sha256(source).hexdigest(),'native_status':native.returncode,'native_stdout':base64.b64encode(native.stdout).decode(),'native_stderr':base64.b64encode(native.stderr).decode(),'expected':expected}
                if name.endswith('/read') or name.endswith('/array'):
                    kind,form=name.split('/')
                    execution=subprocess.run([str(types.PHP),'-n',*types.FLAGS,str(path)],capture_output=True,env=types.ENV,timeout=10)
                    assert execution.returncode==0 and execution.stderr==b'',execution
                    value=execution.stdout[1:-1] if form=='read' else execution.stdout
                    term='PINT '+value.decode() if kind=='LINE' else 'PSTRING ('+types.byte_expr(value.decode('utf8','surrogateescape'))+')'
                    checks+=['P.FOLD.FILE = ('+types.byte_expr(str(path))+')','P.FOLD.CWD = eps']
                    if form=='read':checks+=['P.FOLD.FACTS = eps','$ppmemo_at(P.EXPRESSIONS, [PCINDEX 0, PCFIELD 0, PCINDEX 1]) = ((1, ('+term+')))']
                    else:checks+=['$pffact(P.FOLD.FACTS, [PCINDEX 0, PCFIELD 0, PCFIELD 1, PCFIELD 0, PCINDEX 0, PCFIELD 1]) = ('+term+')']
                    row['execution_stdout']=base64.b64encode(execution.stdout).decode()
                    if form=='read':
                        for label,line in [('absent',None),('zero','0'),('negative','-1'),('positive','99')]:
                            edited=copy.deepcopy(ast);node=magic_node(edited)
                            if line is None:node['meta'].pop('startLine')
                            else:node['meta']['startLine']={'int':line}
                            if label=='positive':
                                v='PINT 99' if kind=='LINE' else term
                                assertions=['P.COMPLETION = PPCNORMAL','$ppmemo_at(P.EXPRESSIONS, [PCINDEX 0, PCFIELD 0, PCINDEX 1]) = ((99, ('+v+')))']
                            else:assertions=['P.COMPLETION = PPCABRUPT (UNSUPPORTED text)']
                            add(name+'/'+label,edited,path,assertions)
                add(name,ast,path,checks);records.append(row)
            source=parse(b'<?php __DIR__;')
            for name,file,cwd,value in [
                ('absent','basename.php','eps',None),
                ('present','basename.php','([47,99,119,100])','[47,99,119,100]'),
                ('binary','basename.php','([47,255])','[47,255]'),
                ('root','basename.php','([47])','[47]'),
                ('absolute','/source/file.php','([47,111,116,104,101,114])','[47,115,111,117,114,99,101]'),
                ('empty','basename.php','(eps)',None),
                ('nul','basename.php','([47,0])',None),
            ]:
                checks=['P.COMPLETION = PPCABRUPT (UNSUPPORTED text)'] if value is None else ['P.COMPLETION = PPCNORMAL','$ppmemo_at(P.EXPRESSIONS, [PCINDEX 0, PCFIELD 0]) = ((1, (PSTRING ('+value+'))))']
                add('directory/'+name,source,file,checks,cwd)
            for name,source in DECLARATIONS.items():add('pending/'+name,parse(source),'/declaration.php',['P.COMPLETION = PPCABRUPT (UNSUPPORTED text)'])
            for name,source in [('line',b'<?php false&&__LINE__;'),('file',b'<?php true||__FILE__;'),('array',b'<?php false&&[__DIR__];')]:
                ast=parse(source);magic_node(ast)['meta'].pop('startLine');add('skipped/'+name,ast,'/skip.php',['P.COMPLETION = PPCNORMAL'])
            fixture=work/'check.watsup';fixture.write_text(compiler.PREFIX+'\n'.join(fixtures)+'\ndec $main() : bool\ndef $main() = true\n'+''.join(f'  -- if $case{i}()\n' for i in range(len(fixtures))))
            run=subprocess.run([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),*map(str,compiler.SPECS),str(fixture)],capture_output=True,text=True,timeout=180)
            if run.returncode!=0 or run.stdout.strip()!='true':
                failure=Path(tempfile.mkdtemp(prefix='magic-compiler-failure-',dir=ROOT/'.tools'))
                (failure/'results.json').write_text(json.dumps({'fingerprint':before,'records':records,'boundaries':boundaries,'fixture':fixture.read_text(),'status':run.returncode,'stdout':run.stdout,'stderr':run.stderr},indent=2)+'\n')
                raise AssertionError((str(failure),run.stdout,run.stderr))
    finally:frontend.close();adapter.close()
    assert before==inputs(),'inputs changed during magic compiler checks'
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({'scope':'Top-level and named-function magic; class, trait and closure declarations remain explicit pending boundaries','fingerprint':before,'profile':types.PROFILE,'records':records,'boundaries':boundaries,'fixtures':len(fixtures)},indent=2)+'\n')
    print(f'Magic compiler: {len(records)} native lints,18 operand/fact checks,36 metadata,7 directory,4 named-function context,3 pending declaration and3 skipped controls passed')

if __name__=='__main__':main()
