#!/usr/bin/env python3
"""Isset/empty compiler access, known results, effects and checked metadata."""
import base64,copy,hashlib,json,subprocess,tempfile
from pathlib import Path
import source_compiler as compiler
from source_compiler import types,context
ROOT=Path(__file__).resolve().parents[2]
REPORT=ROOT/'coverage/semantics/isset-empty-compiler.json'

SOURCES = [('isset-scalar', b'<?php echo isset(1);'),
 ('isset-array-error', b'<?php echo isset([[]=>1]);'),
 ('isset-call', b'<?php echo isset(foo([[]=>1]));'),
 ('isset-method', b'<?php echo isset($x->foo([[]=>1]));'),
 ('isset-list-effect', b'<?php echo isset((list($a)=[1]));'),
 ('isset-globals', b'<?php echo isset($GLOBALS);'),
 ('empty-globals', b'<?php echo empty($GLOBALS);'),
 ('isset-globals-concat', b'<?php echo isset(${"GLO"."BALS"});'),
 ('empty-globals-concat', b'<?php echo empty(${"GLO"."BALS"});'),
 ('isset-globals-temp', b'<?php echo isset(${true?"GLOBALS":"x"});'),
 ('empty-globals-temp', b'<?php echo empty(${true?"GLOBALS":"x"});'),
 ('isset-globals-hole', b'<?php isset($GLOBALS)||[,$x];'),
 ('empty-globals-hole', b'<?php empty($GLOBALS)&&[,$x];'),
 ('isset-globals-prepass', b'<?php [isset($GLOBALS),,];'),
 ('empty-globals-prepass', b'<?php [empty($GLOBALS),,];'),
 ('isset-multi-globals', b'<?php echo isset($GLOBALS,$GLOBALS);'),
 ('isset-multi-missing', b'<?php echo isset($missing,$a[$k++]);echo $k;'),
 ('isset-multi-invalid', b'<?php echo isset($missing,foo());'),
 ('isset-multi-global-invalid', b'<?php echo isset($GLOBALS,1);'),
 ('isset-multi-key-error', b'<?php echo isset($missing,$a[[[]=>1]]);'),
 ('empty-scalar', b'<?php echo empty(1);'),
 ('empty-array-error', b'<?php echo empty([[]=>1]);'),
 ('empty-literal', b'<?php echo empty([]);'),
 ('empty-nan', b'<?php echo empty(NAN);'),
 ('empty-list-effect', b'<?php echo empty((list($a)=[1]));echo $a;'),
 ('empty-list-selected', b'<?php empty((list($a)=[]))||[,$x];'),
 ('empty-list-unselected', b'<?php empty((list($a)=[1]))||[,$x];'),
 ('isset-global-empty-key', b'<?php echo isset($GLOBALS[]);'),
 ('empty-global-empty-key', b'<?php echo empty($GLOBALS[]);'),
 ('isset-global-array-key', b'<?php echo isset($GLOBALS[[]]);'),
 ('empty-global-array-key', b'<?php echo empty($GLOBALS[[]]);'),
 ('isset-header', b'<?php echo isset($http_response_header);echo $http_response_header;'),
 ('empty-header', b'<?php echo empty($http_response_header);echo $http_response_header;'),
 ('isset-name-array', b'<?php echo isset(${[]});'),
 ('empty-name-array', b'<?php echo empty(${[]});'),
 ('isset-lines', b'<?php echo isset(\n1\n);'),
 ('empty-lines', b'<?php echo empty(\n[[]=>1]\n);'),
 ('isset-null-null', b'<?php $a=null;$k=null;echo isset($a[$k]);'),
 ('empty-null-null', b'<?php $a=null;$k=null;echo empty($a[$k]);'),
 ('isset-null-false', b'<?php $a=null;$k=false;echo isset($a[$k]);'),
 ('empty-null-false', b'<?php $a=null;$k=false;echo empty($a[$k]);'),
 ('isset-null-true', b'<?php $a=null;$k=true;echo isset($a[$k]);'),
 ('empty-null-true', b'<?php $a=null;$k=true;echo empty($a[$k]);'),
 ('isset-null-0', b'<?php $a=null;$k=0;echo isset($a[$k]);'),
 ('empty-null-0', b'<?php $a=null;$k=0;echo empty($a[$k]);'),
 ('isset-null--1', b'<?php $a=null;$k=-1;echo isset($a[$k]);'),
 ('empty-null--1', b'<?php $a=null;$k=-1;echo empty($a[$k]);'),
 ('isset-null-99', b'<?php $a=null;$k=99;echo isset($a[$k]);'),
 ('empty-null-99', b'<?php $a=null;$k=99;echo empty($a[$k]);'),
 ('isset-null-1.5', b'<?php $a=null;$k=1.5;echo isset($a[$k]);'),
 ('empty-null-1.5', b'<?php $a=null;$k=1.5;echo empty($a[$k]);'),
 ('isset-null-NAN', b'<?php $a=null;$k=NAN;echo isset($a[$k]);'),
 ('empty-null-NAN', b'<?php $a=null;$k=NAN;echo empty($a[$k]);'),
 ('isset-null-"0x"', b'<?php $a=null;$k="0x";echo isset($a[$k]);'),
 ('empty-null-"0x"', b'<?php $a=null;$k="0x";echo empty($a[$k]);'),
 ('isset-null-" 0"', b'<?php $a=null;$k=" 0";echo isset($a[$k]);'),
 ('empty-null-" 0"', b'<?php $a=null;$k=" 0";echo empty($a[$k]);'),
 ('isset-null-[]', b'<?php $a=null;$k=[];echo isset($a[$k]);'),
 ('empty-null-[]', b'<?php $a=null;$k=[];echo empty($a[$k]);'),
 ('isset-false-null', b'<?php $a=false;$k=null;echo isset($a[$k]);'),
 ('empty-false-null', b'<?php $a=false;$k=null;echo empty($a[$k]);'),
 ('isset-false-false', b'<?php $a=false;$k=false;echo isset($a[$k]);'),
 ('empty-false-false', b'<?php $a=false;$k=false;echo empty($a[$k]);'),
 ('isset-false-true', b'<?php $a=false;$k=true;echo isset($a[$k]);'),
 ('empty-false-true', b'<?php $a=false;$k=true;echo empty($a[$k]);'),
 ('isset-false-0', b'<?php $a=false;$k=0;echo isset($a[$k]);'),
 ('empty-false-0', b'<?php $a=false;$k=0;echo empty($a[$k]);'),
 ('isset-false--1', b'<?php $a=false;$k=-1;echo isset($a[$k]);'),
 ('empty-false--1', b'<?php $a=false;$k=-1;echo empty($a[$k]);'),
 ('isset-false-99', b'<?php $a=false;$k=99;echo isset($a[$k]);'),
 ('empty-false-99', b'<?php $a=false;$k=99;echo empty($a[$k]);'),
 ('isset-false-1.5', b'<?php $a=false;$k=1.5;echo isset($a[$k]);'),
 ('empty-false-1.5', b'<?php $a=false;$k=1.5;echo empty($a[$k]);'),
 ('isset-false-NAN', b'<?php $a=false;$k=NAN;echo isset($a[$k]);'),
 ('empty-false-NAN', b'<?php $a=false;$k=NAN;echo empty($a[$k]);'),
 ('isset-false-"0x"', b'<?php $a=false;$k="0x";echo isset($a[$k]);'),
 ('empty-false-"0x"', b'<?php $a=false;$k="0x";echo empty($a[$k]);'),
 ('isset-false-" 0"', b'<?php $a=false;$k=" 0";echo isset($a[$k]);'),
 ('empty-false-" 0"', b'<?php $a=false;$k=" 0";echo empty($a[$k]);'),
 ('isset-false-[]', b'<?php $a=false;$k=[];echo isset($a[$k]);'),
 ('empty-false-[]', b'<?php $a=false;$k=[];echo empty($a[$k]);'),
 ('isset-true-null', b'<?php $a=true;$k=null;echo isset($a[$k]);'),
 ('empty-true-null', b'<?php $a=true;$k=null;echo empty($a[$k]);'),
 ('isset-true-false', b'<?php $a=true;$k=false;echo isset($a[$k]);'),
 ('empty-true-false', b'<?php $a=true;$k=false;echo empty($a[$k]);'),
 ('isset-true-true', b'<?php $a=true;$k=true;echo isset($a[$k]);'),
 ('empty-true-true', b'<?php $a=true;$k=true;echo empty($a[$k]);'),
 ('isset-true-0', b'<?php $a=true;$k=0;echo isset($a[$k]);'),
 ('empty-true-0', b'<?php $a=true;$k=0;echo empty($a[$k]);'),
 ('isset-true--1', b'<?php $a=true;$k=-1;echo isset($a[$k]);'),
 ('empty-true--1', b'<?php $a=true;$k=-1;echo empty($a[$k]);'),
 ('isset-true-99', b'<?php $a=true;$k=99;echo isset($a[$k]);'),
 ('empty-true-99', b'<?php $a=true;$k=99;echo empty($a[$k]);'),
 ('isset-true-1.5', b'<?php $a=true;$k=1.5;echo isset($a[$k]);'),
 ('empty-true-1.5', b'<?php $a=true;$k=1.5;echo empty($a[$k]);'),
 ('isset-true-NAN', b'<?php $a=true;$k=NAN;echo isset($a[$k]);'),
 ('empty-true-NAN', b'<?php $a=true;$k=NAN;echo empty($a[$k]);'),
 ('isset-true-"0x"', b'<?php $a=true;$k="0x";echo isset($a[$k]);'),
 ('empty-true-"0x"', b'<?php $a=true;$k="0x";echo empty($a[$k]);'),
 ('isset-true-" 0"', b'<?php $a=true;$k=" 0";echo isset($a[$k]);'),
 ('empty-true-" 0"', b'<?php $a=true;$k=" 0";echo empty($a[$k]);'),
 ('isset-true-[]', b'<?php $a=true;$k=[];echo isset($a[$k]);'),
 ('empty-true-[]', b'<?php $a=true;$k=[];echo empty($a[$k]);'),
 ('isset-7-null', b'<?php $a=7;$k=null;echo isset($a[$k]);'),
 ('empty-7-null', b'<?php $a=7;$k=null;echo empty($a[$k]);'),
 ('isset-7-false', b'<?php $a=7;$k=false;echo isset($a[$k]);'),
 ('empty-7-false', b'<?php $a=7;$k=false;echo empty($a[$k]);'),
 ('isset-7-true', b'<?php $a=7;$k=true;echo isset($a[$k]);'),
 ('empty-7-true', b'<?php $a=7;$k=true;echo empty($a[$k]);'),
 ('isset-7-0', b'<?php $a=7;$k=0;echo isset($a[$k]);'),
 ('empty-7-0', b'<?php $a=7;$k=0;echo empty($a[$k]);'),
 ('isset-7--1', b'<?php $a=7;$k=-1;echo isset($a[$k]);'),
 ('empty-7--1', b'<?php $a=7;$k=-1;echo empty($a[$k]);'),
 ('isset-7-99', b'<?php $a=7;$k=99;echo isset($a[$k]);'),
 ('empty-7-99', b'<?php $a=7;$k=99;echo empty($a[$k]);'),
 ('isset-7-1.5', b'<?php $a=7;$k=1.5;echo isset($a[$k]);'),
 ('empty-7-1.5', b'<?php $a=7;$k=1.5;echo empty($a[$k]);'),
 ('isset-7-NAN', b'<?php $a=7;$k=NAN;echo isset($a[$k]);'),
 ('empty-7-NAN', b'<?php $a=7;$k=NAN;echo empty($a[$k]);'),
 ('isset-7-"0x"', b'<?php $a=7;$k="0x";echo isset($a[$k]);'),
 ('empty-7-"0x"', b'<?php $a=7;$k="0x";echo empty($a[$k]);'),
 ('isset-7-" 0"', b'<?php $a=7;$k=" 0";echo isset($a[$k]);'),
 ('empty-7-" 0"', b'<?php $a=7;$k=" 0";echo empty($a[$k]);'),
 ('isset-7-[]', b'<?php $a=7;$k=[];echo isset($a[$k]);'),
 ('empty-7-[]', b'<?php $a=7;$k=[];echo empty($a[$k]);'),
 ('isset-"ab"-null', b'<?php $a="ab";$k=null;echo isset($a[$k]);'),
 ('empty-"ab"-null', b'<?php $a="ab";$k=null;echo empty($a[$k]);'),
 ('isset-"ab"-false', b'<?php $a="ab";$k=false;echo isset($a[$k]);'),
 ('empty-"ab"-false', b'<?php $a="ab";$k=false;echo empty($a[$k]);'),
 ('isset-"ab"-true', b'<?php $a="ab";$k=true;echo isset($a[$k]);'),
 ('empty-"ab"-true', b'<?php $a="ab";$k=true;echo empty($a[$k]);'),
 ('isset-"ab"-0', b'<?php $a="ab";$k=0;echo isset($a[$k]);'),
 ('empty-"ab"-0', b'<?php $a="ab";$k=0;echo empty($a[$k]);'),
 ('isset-"ab"--1', b'<?php $a="ab";$k=-1;echo isset($a[$k]);'),
 ('empty-"ab"--1', b'<?php $a="ab";$k=-1;echo empty($a[$k]);'),
 ('isset-"ab"-99', b'<?php $a="ab";$k=99;echo isset($a[$k]);'),
 ('empty-"ab"-99', b'<?php $a="ab";$k=99;echo empty($a[$k]);'),
 ('isset-"ab"-1.5', b'<?php $a="ab";$k=1.5;echo isset($a[$k]);'),
 ('empty-"ab"-1.5', b'<?php $a="ab";$k=1.5;echo empty($a[$k]);'),
 ('isset-"ab"-NAN', b'<?php $a="ab";$k=NAN;echo isset($a[$k]);'),
 ('empty-"ab"-NAN', b'<?php $a="ab";$k=NAN;echo empty($a[$k]);'),
 ('isset-"ab"-"0x"', b'<?php $a="ab";$k="0x";echo isset($a[$k]);'),
 ('empty-"ab"-"0x"', b'<?php $a="ab";$k="0x";echo empty($a[$k]);'),
 ('isset-"ab"-" 0"', b'<?php $a="ab";$k=" 0";echo isset($a[$k]);'),
 ('empty-"ab"-" 0"', b'<?php $a="ab";$k=" 0";echo empty($a[$k]);'),
 ('isset-"ab"-[]', b'<?php $a="ab";$k=[];echo isset($a[$k]);'),
 ('empty-"ab"-[]', b'<?php $a="ab";$k=[];echo empty($a[$k]);'),
 ('isset-[]-null', b'<?php $a=[];$k=null;echo isset($a[$k]);'),
 ('empty-[]-null', b'<?php $a=[];$k=null;echo empty($a[$k]);'),
 ('isset-[]-false', b'<?php $a=[];$k=false;echo isset($a[$k]);'),
 ('empty-[]-false', b'<?php $a=[];$k=false;echo empty($a[$k]);'),
 ('isset-[]-true', b'<?php $a=[];$k=true;echo isset($a[$k]);'),
 ('empty-[]-true', b'<?php $a=[];$k=true;echo empty($a[$k]);'),
 ('isset-[]-0', b'<?php $a=[];$k=0;echo isset($a[$k]);'),
 ('empty-[]-0', b'<?php $a=[];$k=0;echo empty($a[$k]);'),
 ('isset-[]--1', b'<?php $a=[];$k=-1;echo isset($a[$k]);'),
 ('empty-[]--1', b'<?php $a=[];$k=-1;echo empty($a[$k]);'),
 ('isset-[]-99', b'<?php $a=[];$k=99;echo isset($a[$k]);'),
 ('empty-[]-99', b'<?php $a=[];$k=99;echo empty($a[$k]);'),
 ('isset-[]-1.5', b'<?php $a=[];$k=1.5;echo isset($a[$k]);'),
 ('empty-[]-1.5', b'<?php $a=[];$k=1.5;echo empty($a[$k]);'),
 ('isset-[]-NAN', b'<?php $a=[];$k=NAN;echo isset($a[$k]);'),
 ('empty-[]-NAN', b'<?php $a=[];$k=NAN;echo empty($a[$k]);'),
 ('isset-[]-"0x"', b'<?php $a=[];$k="0x";echo isset($a[$k]);'),
 ('empty-[]-"0x"', b'<?php $a=[];$k="0x";echo empty($a[$k]);'),
 ('isset-[]-" 0"', b'<?php $a=[];$k=" 0";echo isset($a[$k]);'),
 ('empty-[]-" 0"', b'<?php $a=[];$k=" 0";echo empty($a[$k]);'),
 ('isset-[]-[]', b'<?php $a=[];$k=[];echo isset($a[$k]);'),
 ('empty-[]-[]', b'<?php $a=[];$k=[];echo empty($a[$k]);'),
 ('isset-globals', b'<?php isset($GLOBALS);'),
 ('empty-globals', b'<?php empty($GLOBALS);'),
 ('isset-two-globals', b'<?php isset($GLOBALS,$GLOBALS);'),
 ('isset-variable', b'<?php isset($a);'),
 ('isset-mixed', b'<?php isset($GLOBALS,$a);'),
 ('empty-literal', b'<?php empty([]);'),
 ('empty-list-effect', b'<?php empty((list($a)=[]));'),
 ('empty-cast-list', b'<?php empty((bool)(list($a)=[]));'),
 ('empty-coalesce-list', b'<?php empty((list($a)=[])??[1]);'),
 ('empty-comparison-list', b'<?php empty((list($a)=[])===[]);'),
 ('isset-globals-skip', b'<?php isset($GLOBALS)||[,$x];'),
 ('isset-two-skip', b'<?php isset($GLOBALS,$GLOBALS)||[,$x];'),
 ('isset-mixed-visit', b'<?php isset($GLOBALS,$a)||[,$x];'),
 ('empty-list-skip', b'<?php empty((list($a)=[]))||[,$x];'),
 ('empty-cast-visit', b'<?php empty((bool)(list($a)=[]))||[,$x];'),
 ('empty-prepass-barrier', b'<?php [empty([[]=>1]),,];'),
 ('second-argument-line', b'<?php isset($a,\n$b[\n]);'),
 ('second-argument-name', b'<?php isset($a,\n${[1]});'),
 ('nonvariable-priority', b'<?php isset([[]=>1]);')]

BOUNDARIES = [('isset-globals', b'<?php isset($GLOBALS);', ['P.FOLD.VALUE = (PBOOL true)']),
 ('empty-globals', b'<?php empty($GLOBALS);', ['P.FOLD.VALUE = (PBOOL false)']),
 ('isset-two-globals', b'<?php isset($GLOBALS,$GLOBALS);', ['P.FOLD.VALUE = (PBOOL true)']),
 ('isset-variable',
  b'<?php isset($a);',
  ['P.FOLD.VALUE = eps', '$ppaccess(P, [PCINDEX 0, PCFIELD 0, PCFIELD 0, PCINDEX 0]) = (PPIS)']),
 ('isset-mixed', b'<?php isset($GLOBALS,$a);', ['P.FOLD.VALUE = eps']),
 ('empty-literal', b'<?php empty([]);', ['P.FOLD.VALUE = (PBOOL true)']),
 ('empty-list-effect',
  b'<?php empty((list($a)=[]));',
  ['P.FOLD.VALUE = (PBOOL true)', '$ieeffect(P.EXPRESSIONS, [PCINDEX 0, PCFIELD 0, PCFIELD 0])']),
 ('empty-cast-list',
  b'<?php empty((bool)(list($a)=[]));',
  ['P.FOLD.VALUE = eps', '$ieeffect(P.EXPRESSIONS, [PCINDEX 0, PCFIELD 0, PCFIELD 0, PCFIELD 0])']),
 ('empty-coalesce-list', b'<?php empty((list($a)=[])??[1]);', ['P.FOLD.VALUE = eps']),
 ('empty-comparison-list', b'<?php empty((list($a)=[])===[]);', ['P.FOLD.VALUE = (PBOOL false)'])]

PENDING = [('empty-call-pending', b'<?php echo empty(foo());'),
 ('isset-nullsafe-pending', b'<?php echo isset($x?->p);')]

PREFIX = compiler.PREFIX + r"""
dec $ieeffect(ppexprdone*, pcpath) : bool
def $ieeffect(eps, pcpath) = false
def $ieeffect((PPCEFFECT pcpath) :: ppexprdone*, pcpath) = true
def $ieeffect((PPCEFFECT pcpath_other) :: ppexprdone*, pcpath) = $ieeffect(ppexprdone*, pcpath)
  -- if pcpath_other =/= pcpath
def $ieeffect((PPCEXPR pcpath_other n pvalue?) :: ppexprdone*, pcpath) = $ieeffect(ppexprdone*, pcpath)
"""

def inputs():
    paths=[*compiler.SPECS,Path(__file__),ROOT/'frontend/worker.php',ROOT/'spec/schema.json',
           types.PHP,ROOT/'.tools/php-file.so',ROOT/'_build/default/adapter/main.exe',
           ROOT/'tests/semantics/_build/default/numeric_runner.exe']
    return {'closure':types.syntax_validation.implementation_fingerprint(),
            'direct':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}


def main():
    before=inputs();fixtures=[];records=[];boundaries=[];metadata=[];pending=[]
    frontend=types.Worker([str(types.PHP),'-n','-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')])
    adapter=types.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    def checked(source):
        parsed=frontend.request({'op':'parse','source':base64.b64encode(source).decode()})
        assert parsed['accepted'],parsed
        result=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
        assert result['ok'],result
        return result['fixture']
    def add(fixture,path,checks):
        n=len(fixtures)
        fixtures.append(f'dec $case{n}() : bool\ndef $case{n}() = true\n  -- if P = $ppstart(91, '+fixture+', '+types.byte_expr(str(path))+')\n'+''.join('  -- if '+check+'\n' for check in checks))
    try:
        with tempfile.TemporaryDirectory(prefix='php-isset-empty-compiler-',dir=ROOT/'.tools') as directory:
            work=Path(directory).resolve()
            for i,(name,source) in enumerate(SOURCES):
                path=work/f'source-{i}.php';path.write_bytes(source)
                command=[str(types.PHP),'-n',*types.FLAGS,'-l',str(path)]
                native=subprocess.run(command,capture_output=True,env=types.ENV,timeout=10)
                expected=context.expected_events(context.events(native),path)
                add(checked(source),path,['$pptrace(P) = '+expected])
                records.append({'id':name,'source_sha256':hashlib.sha256(source).hexdigest(),'native_status':native.returncode,'native_stdout':base64.b64encode(native.stdout).decode(),'native_stderr':base64.b64encode(native.stderr).decode(),'expected':expected})
            for i,(name,source,checks) in enumerate(BOUNDARIES):
                path=work/f'metadata-{i}.php';path.write_bytes(source)
                add(checked(source),path,['P.COMPLETION = PPCNORMAL',*checks])
                boundaries.append({'id':name,'source_sha256':hashlib.sha256(source).hexdigest(),'checks':checks})
            parsed=frontend.request({'op':'parse','source':base64.b64encode(b'<?php isset($a);').decode()})
            assert parsed['accepted'],parsed
            for value in [None,0,-1,91]:
                for which in ['first','second']:
                    edited=copy.deepcopy(parsed['ast']);items=edited['program'][0]['fields'][0]['fields'][0]
                    if which=='second':items.append(copy.deepcopy(items[0]));items[-1]['fields'][0]={'bytes':'Yg=='}
                    if value is None:items[-1]['meta'].pop('startLine')
                    else:items[-1]['meta']['startLine']={'int':str(value)}
                    result=adapter.request({'op':'check','ast':edited,'fixture':True});assert result['ok'],result
                    checks=['P.COMPLETION = PPCNORMAL','P.LOCATION.LINE = 91'] if value==91 else ['P.COMPLETION = PPCABRUPT (UNSUPPORTED "missing ordinary compiler line")']
                    add(result['fixture'],work/'metadata.php',checks);metadata.append({'id':which+'-'+str(value),'checks':checks})
            for kind in ['missing-root-line','empty-typed-list']:
                edited=copy.deepcopy(parsed['ast']);expression=edited['program'][0]['fields'][0]
                if kind=='missing-root-line':expression['meta'].pop('startLine');checks=['P.COMPLETION = PPCNORMAL']
                else:expression['fields'][0]=[];checks=['P.COMPLETION = PPCABRUPT (UNSUPPORTED "missing ordinary compiler line")']
                result=adapter.request({'op':'check','ast':edited,'fixture':True});assert result['ok'],result
                add(result['fixture'],work/'metadata.php',checks);metadata.append({'id':kind,'checks':checks})
            for name,source in PENDING:
                path=work/(name+'.php');path.write_bytes(source)
                add(checked(source),path,['P.COMPLETION = PPCABRUPT (UNSUPPORTED "ordinary expression or writable operand compilation")'])
                pending.append({'id':name,'source_sha256':hashlib.sha256(source).hexdigest()})
            fixture=work/'check.watsup' ;fixture.write_text(PREFIX+'\n'.join(fixtures)+'\ndec $main() : bool\ndef $main() = true\n'+''.join(f'  -- if $case{i}()\n' for i in range(len(fixtures))))
            run=subprocess.run([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),*map(str,compiler.SPECS),str(fixture)],capture_output=True,text=True,timeout=180)
            if run.returncode!=0 or run.stdout.strip()!='true':
                failure=Path(tempfile.mkdtemp(prefix='isset-empty-compiler-failure-',dir=ROOT/'.tools'))
                (failure/'results.json').write_text(json.dumps({'fingerprint':before,'records':records,'boundaries':boundaries,'metadata':metadata,'pending':pending,'fixture':fixture.read_text(),'status':run.returncode,'stdout':run.stdout,'stderr':run.stderr},indent=2)+'\n')
                raise AssertionError((str(failure),run.stdout,run.stderr))
    finally:
        frontend.close();adapter.close()
    assert before==inputs(),'inputs changed during isset/empty compiler checks'
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({'scope':'188 exact isset/empty compiler traces,10 known/access/effect controls,10 edited metadata boundaries and2 explicit pending call/object cases; runtime execution tested separately','fingerprint':before,'profile':types.PROFILE,'records':records,'boundaries':boundaries,'metadata':metadata,'pending':pending},indent=2)+'\n')
    print('Isset/empty compiler: 188 native lints,10 known/access/effect,10 metadata and2 explicit pending controls passed')

if __name__=='__main__':
    main()
