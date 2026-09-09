#!/usr/bin/env python3
"""Checked-source comparisons, numeric scanner provenance and operand ownership."""
import base64, hashlib, json, random, re, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/semantics'))
import static_types as types

pairs=[
 ('NAN',v) for v in ['null','false','true','0','NAN','[]','[NAN]','""','"abc"','"NAN"']
]+[(a,b) for a,b in [('[1]','[2]'),('["x"=>1]','["y"=>1]'),('[1=>1,0=>2]','[0=>2,1=>1]'),('[1]','["1"]'),('"9223372036854775807"','"9223372036854775808"'),('"9223372036854775808"','"9223372036854775809"'),('"09223372036854775808"','"9223372036854775808"'),('"9223372036854775808.0"','"9223372036854775809"'),('"-9223372036854775808"','"-9223372036854775809"'),('"1e999"','"2e999"'),('"1e999"','"1e1000"'),('"1e999"','"1E999"'),('null','"0"'),('false','"0"'),('INF','"INF"'),('PHP_INT_MAX','"9223372036854775808"')]]
pairs += [
 ('"9223372036854775808\\0"', '"9223372036854775808"'),
 ('"10000000000000000000e-19x"', '"2"'),
 ('"10000000000000000000e-"', '"2"'),
 ('"  00010000000000000000000e-19\\t"', '"2"'),
 ('"-0"', '"0.0"'),
]
values=['null','false','true','0','1','-1','PHP_INT_MAX','PHP_INT_MIN','0.0','-0.0','NAN','INF','-INF','1.5','""','"0"','"1"','"1x"','" 1 "','"01"','[]','[0]','[1]','[NAN]','["x"=>1]','[[1]]']
rng=random.Random(8501052)
pairs += [(rng.choice(values),rng.choice(values)) for _ in range(65)]
OPERATORS=['<=>','==','!=','<','<=','>','>=']
NORMAL_CASES={}
for index,(left,right) in enumerate(pairs):
 expressions=[f'($a {op} $b)' for op in OPERATORS]+[f'($b {op} $a)' for op in OPERATORS]
 NORMAL_CASES[f'pair-{index}']=('<?php $a='+left+';$b='+right+';echo '+',":",'.join(expressions)+';').encode()
for i,(left,right) in enumerate(pairs[:26]):
 NORMAL_CASES[f'prepass-{i}']=('<?php $a=['+','.join('('+left+op+right+')' for op in OPERATORS)+'];echo '+',":",'.join('$a['+str(j)+']' for j in range(7))+';').encode()

for index,left in enumerate(['10000000000000000000e-19','-10000000000000000000e-19','1000000000000000000e-18','10000000000000000000.0','00010000000000000000000e-19','+00010000000000000000000e-19','-00010000000000000000000e-19','9223372036854775808e-18','9223372036854775808.0','9223372036854775808 ','-9223372036854775808 ','10000000000000000000e-999','-10000000000000000000e-999',' 10000000000000000000e-19 ','1e999','2e999','10000000000000000001e-19','9223372036854775807e-18']):
 for j,right in enumerate(['2','-2','1.0','-1.0','10000000000000000001e-19']):
  expressions=[f'($a {op} $b)' for op in OPERATORS]+[f'($b {op} $a)' for op in OPERATORS]
  NORMAL_CASES[f'overflow-{index}-{j}']=('<?php $a='+repr(left)+';$b='+repr(right)+';echo '+',":",'.join(expressions)+';').encode()


NORMAL_CASES.update({
 'same-nan-array': b'<?php $a=[NAN];$b=$a;echo $a==$b,":",$a<=>$b; $b[1]=1;unset($b[1]);echo ":",$a<=>$b,":",$b<=>$a;',
 'loop-pool-comparison': b'<?php $i=0;$a=[NAN];while($i<3){$b=[NAN];echo $a==$b,":",$a<=>$b,";";$a=$b;$i=$i+1;}',
 'recursive-same-nested': b'<?php $a=[];$a[0]=&$a;$b=[$a];echo $a<=>$b;',
 'recursive-same': b'<?php $a=[];$a[0]=&$a;echo $a==$a,":",$a<=>$a;',
 'recursive-count': b'<?php $a=[];$a[0]=&$a;$b=[];$b[0]=&$b;$b[1]=1;echo $a<=>$b,":",$b<=>$a;',
 'recursive-key': b'<?php $a=[];$a[0]=&$a;$b=[];$b[1]=&$b;echo $a<=>$b,":",$b<=>$a;',
 'recursive-value-first': b'<?php $a=[0];$a[1]=&$a;$b=[1];$b[1]=&$b;echo $a<=>$b,":",$b<=>$a;',
 'delayed-greater': b'<?php $a=1;echo $a>($a=2),":",$a>=($a=3),":",$a;',
 'captured-greater': b'<?php $a=1;$n="a";echo $$n>($a=2),":",$$n>=($a=3),":",$a;',
 'reference-greater': b'<?php $a=1;echo ($r=&$a)>($a=2),":",($r=&$a)>=($a=3),":",$r;',
 'reference-rebinding-greater': b'<?php $x=1;$y=2;echo ($r=&$x)>($x=&$y),":",$r,":",$x;$x=1;echo ($r=&$x)>=($x=&$y);',
 'array-root-replaced-greater': b'<?php $a=[1];echo $a[0]>($a=[0])[0],":",$a[0];',
 'array-delayed-greater': b'<?php $a=[1];echo $a>($a=[2]),":",$a>=($a=[3]);',
 'array-captured-greater': b'<?php $a=[1];$n="a";echo $$n>($a=[2]),":",$$n>=($a=[3]);',
 'dimension-greater': b'<?php $a=[1];echo $a[0]>($a[0]=2),":",$a[0]>=($a[0]=3),":",$a[0];',
 'prepass-delayed-greater': b'<?php $a=1;$b=[(true?$a:0)>($a=2)];echo $b[0],":",$a;',
 'ordinary-selected-greater': b'<?php $a=1;echo (true?$a:0)>($a=2),":",$a;',
 'array-key-order': b'<?php $a=["x"=>1,"y"=>2];$b=["y"=>2,"x"=>1];echo $a==$b,":",$a<=>$b;',
 'array-reference-compare': b'<?php $x=1;$a=[&$x];$b=$a;echo $a<=>$b;$x=2;echo $a<=>[2];',
 'namespace-nan-compare': b'<?php namespace N;$a=[NAN];$b=[NAN];echo NAN==true,":",NAN==null,":",$a<=>$b;',
})
CASES = {'comparison-'+name: source for name,source in NORMAL_CASES.items()}
CASES.update({
 'comparison-recursive-before-count': b'<?php $a=[];$a[0]=&$a;$b=[[]];echo $a<=>$b;',
 'comparison-recursive-error': b'<?php $a=[];$a[0]=&$a;$b=[];$b[0]=&$b;echo "before",$a<=>$b;',
 'comparison-recursive-greater-error': b'<?php $a=[];$a[0]=&$a;$b=[];$b[0]=&$b;echo "before",$a>$b;',
 'comparison-multiline-recursive': b'<?php\n$a=[];$a[0]=&$a;$b=[];$b[0]=&$b;\necho $a\n<=>\n$b;',
})
ARCHIVES=[ROOT/'coverage/semantics/comparison-phase-originals.json', ROOT/'coverage/semantics/comparison-overflow-draft-disagreement.json']
for row in json.loads(ARCHIVES[0].read_text()):
 CASES['comparison-phase-'+row['id']]=base64.b64decode(row['source_base64'])
for row in json.loads(ARCHIVES[1].read_text())['records']:
 CASES['comparison-retained-'+row['id']]=base64.b64decode(row['source_base64'])

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

def fingerprint():
    return {'closure':types.syntax_validation.implementation_fingerprint(),
            'archives':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in ARCHIVES}}

def main():
    subprocess.run([str(ROOT/'scripts/opam-exec.sh'),'dune','build','--root',str(ROOT/'tests/semantics'),'numeric_runner.exe'],cwd=ROOT,check=True,timeout=120)
    runner=ROOT/'tests/semantics/_build/default/numeric_runner.exe'
    specs=[ROOT/p for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
    before=fingerprint()
    frontend=types.Worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')])
    adapter=types.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    records=[]; assertions=[]
    try:
        with tempfile.TemporaryDirectory(dir=ROOT/'.tools') as tmp:
            source_path=Path(tmp)/'comparison.php'
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
                if name in {'loop-pool-comparison','reference-greater','array-reference-compare','recursive-same'}:
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
            for index,checks in enumerate(assertions):
                fixture=Path(tmp)/'comparison.watsup'
                fixture.write_text(PREFIX+'dec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+check+'\n' for check in checks))
                run=subprocess.run([str(runner),*map(str,specs),str(fixture)],capture_output=True,text=True,cwd=ROOT,timeout=120)
                if run.returncode or run.stdout.strip()!='true':
                    (ROOT/'.tools/comparison-failure.watsup').write_text(fixture.read_text())
                    raise AssertionError((index,run.stdout,run.stderr))
    finally:
        frontend.close();adapter.close()
    assert before==fingerprint(),'inputs changed during comparison gate'
    report={'result':'pass','classification':'checked-source six-value comparisons, compiler pools, delayed operands and budget resumption',
            'source_cases':len(records),'state_cases':len(assertions),'assertions':sum(map(len,assertions)),
            'records':records,'fingerprint':before}
    (ROOT/'coverage/semantics/comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    print({key:report[key] for key in ('result','source_cases','state_cases','assertions')})

if __name__=='__main__':
    main()
