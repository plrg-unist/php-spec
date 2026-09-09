#!/usr/bin/env python3
"""Array unpacking: exact source inputs, builder ownership and resumption."""
import base64, json, re, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/semantics'))
import static_types as types

NORMAL_CASES = {
    'unpack-state-0': b'<?php $x=[4=>1,9=>2];$a=[...$x];echo $a[0],$a[1];',
    'unpack-state-1': b'<?php $x=[-5=>1,"k"=>2,12=>3];$a=[9,...$x,4];echo $a[0],$a[1],$a["k"],$a[2],$a[3];',
    'unpack-state-2': b'<?php $x=["k"=>2];$a=["k"=>1,...$x];echo $a["k"];',
    'unpack-state-3': b'<?php $x=["k"=>2];$a=[...$x,"k"=>3];echo $a["k"];',
    'unpack-state-4': b'<?php $x=["k"=>2];$a=[...$x,...$x];echo $a["k"];',
    'unpack-state-5': b'<?php $x=1;$a=[&$x];$b=[...$a];$b[0]=3;echo $x,$a[0],$b[0];',
    'unpack-state-6': b'<?php $x=1;$a=[&$x];unset($x);$b=[...$a];$b[0]=3;echo $a[0],$b[0];',
    'unpack-state-7': b'<?php $x=1;$a=[&$x];$r=&$a[0];unset($x);$b=[...$a];$b[0]=3;echo $r,$a[0],$b[0];',
    'unpack-state-8': b'<?php $x=1;$a=[&$x];unset($x);$b=[...$a,...$a];$b[0]=3;echo $a[0],$b[0],$b[1];',
    'unpack-state-9': b'<?php $x=1;$a=[&$x];unset($x);$b=[...($c=$a)];$b[0]=3;echo $a[0],$c[0],$b[0];',
    'unpack-state-10': b'<?php $a=[];$a[0]=&$a;$b=[...$a];$b[1]=2;echo $a===$b,$b[0]===$a;',
    'unpack-state-11': b'<?php $a=[NAN];$b=[...$a];echo $a===$b;',
    'unpack-state-12': b'<?php $a=[1];$b=[...$a,($a[0]=2)];echo $a[0],$b[0],$b[1];',
    'unpack-state-13': b'<?php $a=[1];$b=[($a[0]=2),...$a];echo $a[0],$b[0],$b[1];',
    'unpack-state-14': b'<?php $a=[1];$b=[...($a=[2]),...$a];echo $a[0],$b[0],$b[1];',
    'unpack-state-15': b'<?php $a=[1];$b=[...($r=&$a),($r[0]=2)];echo $a[0],$b[0],$b[1];',
    'unpack-state-16': b'<?php $a=[PHP_INT_MAX=>1];$b=[...$a,2];echo $b[0],$b[1];',
    'unpack-state-17': b'<?php $a=[1];$b=[PHP_INT_MAX=>2,...$a];echo 7;',
    'unpack-state-18': b'<?php $a=[1];$b=[PHP_INT_MAX=>2,...[],3];echo 7;',
    'unpack-state-19': b'<?php $a=[1];$b=[PHP_INT_MAX=>2,...$a,$missing];echo 7;',
    'unpack-state-20': b'<?php $a=["k"=>1];$b=[PHP_INT_MAX=>2,...$a];echo $b["k"];',
    'unpack-state-21': b'<?php $a=[1];$b=[\n...\n$a\n];echo $b[0];',
    'unpack-state-22': b'<?php $a=[1];$b=[PHP_INT_MAX=>2,\n...\n$a\n];',
    'unpack-state-23': b'<?php $a=[1];$b=[...$missing,$a];',
    'unpack-state-24': b'<?php $a=[1];$b=[...$a,...$missing];',
    'unpack-state-25': b'<?php $a=[1];$b=[...$this];',
    'unpack-state-26': b'<?php $a=[1];$b=[...${true?"this":"x"}];',
    'loop-unpack-0': b'<?php $a=[1];$i=0;while($i++<3){$b=[...$a];$b[0]+=1;echo $a[0],$b[0];}',
    'loop-unpack-1': b'<?php $x=1;$a=[&$x];$i=0;while($i++<3){$b=[...$a];$b[0]+=1;echo $x,$a[0];}',
    'loop-unpack-2': b'<?php $x=1;$a=[&$x];unset($x);$i=0;while($i++<3){$b=[...$a];$b[0]+=1;echo $a[0],$b[0];}',
    'loop-unpack-3': b'<?php $a=[];$a[0]=&$a;$i=0;while($i++<3){$b=[...$a];echo $a===$b;}',
}

CASES = {
    'unpack-unpack-state-0': b'<?php $x=[4=>1,9=>2];$a=[...$x];echo $a[0],$a[1];',
    'unpack-unpack-state-1': b'<?php $x=[-5=>1,"k"=>2,12=>3];$a=[9,...$x,4];echo $a[0],$a[1],$a["k"],$a[2],$a[3];',
    'unpack-unpack-state-2': b'<?php $x=["k"=>2];$a=["k"=>1,...$x];echo $a["k"];',
    'unpack-unpack-state-3': b'<?php $x=["k"=>2];$a=[...$x,"k"=>3];echo $a["k"];',
    'unpack-unpack-state-4': b'<?php $x=["k"=>2];$a=[...$x,...$x];echo $a["k"];',
    'unpack-unpack-state-5': b'<?php $x=1;$a=[&$x];$b=[...$a];$b[0]=3;echo $x,$a[0],$b[0];',
    'unpack-unpack-state-6': b'<?php $x=1;$a=[&$x];unset($x);$b=[...$a];$b[0]=3;echo $a[0],$b[0];',
    'unpack-unpack-state-7': b'<?php $x=1;$a=[&$x];$r=&$a[0];unset($x);$b=[...$a];$b[0]=3;echo $r,$a[0],$b[0];',
    'unpack-unpack-state-8': b'<?php $x=1;$a=[&$x];unset($x);$b=[...$a,...$a];$b[0]=3;echo $a[0],$b[0],$b[1];',
    'unpack-unpack-state-9': b'<?php $x=1;$a=[&$x];unset($x);$b=[...($c=$a)];$b[0]=3;echo $a[0],$c[0],$b[0];',
    'unpack-unpack-state-10': b'<?php $a=[];$a[0]=&$a;$b=[...$a];$b[1]=2;echo $a===$b,$b[0]===$a;',
    'unpack-unpack-state-11': b'<?php $a=[NAN];$b=[...$a];echo $a===$b;',
    'unpack-unpack-state-12': b'<?php $a=[1];$b=[...$a,($a[0]=2)];echo $a[0],$b[0],$b[1];',
    'unpack-unpack-state-13': b'<?php $a=[1];$b=[($a[0]=2),...$a];echo $a[0],$b[0],$b[1];',
    'unpack-unpack-state-14': b'<?php $a=[1];$b=[...($a=[2]),...$a];echo $a[0],$b[0],$b[1];',
    'unpack-unpack-state-15': b'<?php $a=[1];$b=[...($r=&$a),($r[0]=2)];echo $a[0],$b[0],$b[1];',
    'unpack-unpack-state-16': b'<?php $a=[PHP_INT_MAX=>1];$b=[...$a,2];echo $b[0],$b[1];',
    'unpack-unpack-state-17': b'<?php $a=[1];$b=[PHP_INT_MAX=>2,...$a];echo 7;',
    'unpack-unpack-state-18': b'<?php $a=[1];$b=[PHP_INT_MAX=>2,...[],3];echo 7;',
    'unpack-unpack-state-19': b'<?php $a=[1];$b=[PHP_INT_MAX=>2,...$a,$missing];echo 7;',
    'unpack-unpack-state-20': b'<?php $a=["k"=>1];$b=[PHP_INT_MAX=>2,...$a];echo $b["k"];',
    'unpack-unpack-state-21': b'<?php $a=[1];$b=[\n...\n$a\n];echo $b[0];',
    'unpack-unpack-state-22': b'<?php $a=[1];$b=[PHP_INT_MAX=>2,\n...\n$a\n];',
    'unpack-unpack-state-23': b'<?php $a=[1];$b=[...$missing,$a];',
    'unpack-unpack-state-24': b'<?php $a=[1];$b=[...$a,...$missing];',
    'unpack-unpack-state-25': b'<?php $a=[1];$b=[...$this];',
    'unpack-unpack-state-26': b'<?php $a=[1];$b=[...${true?"this":"x"}];',
    'unpack-unpack-value-0-0': b'<?php $x=null;$a=[...$x];echo $a;',
    'unpack-unpack-value-0-1': b'<?php $x=null;$a=[1,...$x,2];echo $a;',
    'unpack-unpack-value-0-2': b'<?php $a=[...null];echo $a;',
    'unpack-unpack-value-0-3': b'<?php $a=1;$b=[$a,...null];echo $b;',
    'unpack-unpack-value-0-4': b'<?php $a=1;$b=[...null,$a];echo $b;',
    'unpack-unpack-value-0-5': b'<?php $a=1;$b=[&$a,...null];echo $b;',
    'unpack-unpack-value-0-6': b'<?php $a=1;$b=[...null,&$a];echo $b;',
    'unpack-unpack-value-0-7': b'<?php echo false && [...null];echo 1;',
    'unpack-unpack-value-0-8': b'<?php $a=[false && [...null]];echo 1;',
    'unpack-unpack-value-1-0': b'<?php $x=false;$a=[...$x];echo $a;',
    'unpack-unpack-value-1-1': b'<?php $x=false;$a=[1,...$x,2];echo $a;',
    'unpack-unpack-value-1-2': b'<?php $a=[...false];echo $a;',
    'unpack-unpack-value-1-3': b'<?php $a=1;$b=[$a,...false];echo $b;',
    'unpack-unpack-value-1-4': b'<?php $a=1;$b=[...false,$a];echo $b;',
    'unpack-unpack-value-1-5': b'<?php $a=1;$b=[&$a,...false];echo $b;',
    'unpack-unpack-value-1-6': b'<?php $a=1;$b=[...false,&$a];echo $b;',
    'unpack-unpack-value-1-7': b'<?php echo false && [...false];echo 1;',
    'unpack-unpack-value-1-8': b'<?php $a=[false && [...false]];echo 1;',
    'unpack-unpack-value-2-0': b'<?php $x=true;$a=[...$x];echo $a;',
    'unpack-unpack-value-2-1': b'<?php $x=true;$a=[1,...$x,2];echo $a;',
    'unpack-unpack-value-2-2': b'<?php $a=[...true];echo $a;',
    'unpack-unpack-value-2-3': b'<?php $a=1;$b=[$a,...true];echo $b;',
    'unpack-unpack-value-2-4': b'<?php $a=1;$b=[...true,$a];echo $b;',
    'unpack-unpack-value-2-5': b'<?php $a=1;$b=[&$a,...true];echo $b;',
    'unpack-unpack-value-2-6': b'<?php $a=1;$b=[...true,&$a];echo $b;',
    'unpack-unpack-value-2-7': b'<?php echo false && [...true];echo 1;',
    'unpack-unpack-value-2-8': b'<?php $a=[false && [...true]];echo 1;',
    'unpack-unpack-value-3-0': b'<?php $x=0;$a=[...$x];echo $a;',
    'unpack-unpack-value-3-1': b'<?php $x=0;$a=[1,...$x,2];echo $a;',
    'unpack-unpack-value-3-2': b'<?php $a=[...0];echo $a;',
    'unpack-unpack-value-3-3': b'<?php $a=1;$b=[$a,...0];echo $b;',
    'unpack-unpack-value-3-4': b'<?php $a=1;$b=[...0,$a];echo $b;',
    'unpack-unpack-value-3-5': b'<?php $a=1;$b=[&$a,...0];echo $b;',
    'unpack-unpack-value-3-6': b'<?php $a=1;$b=[...0,&$a];echo $b;',
    'unpack-unpack-value-3-7': b'<?php echo false && [...0];echo 1;',
    'unpack-unpack-value-3-8': b'<?php $a=[false && [...0]];echo 1;',
    'unpack-unpack-value-4-0': b'<?php $x=1.5;$a=[...$x];echo $a;',
    'unpack-unpack-value-4-1': b'<?php $x=1.5;$a=[1,...$x,2];echo $a;',
    'unpack-unpack-value-4-2': b'<?php $a=[...1.5];echo $a;',
    'unpack-unpack-value-4-3': b'<?php $a=1;$b=[$a,...1.5];echo $b;',
    'unpack-unpack-value-4-4': b'<?php $a=1;$b=[...1.5,$a];echo $b;',
    'unpack-unpack-value-4-5': b'<?php $a=1;$b=[&$a,...1.5];echo $b;',
    'unpack-unpack-value-4-6': b'<?php $a=1;$b=[...1.5,&$a];echo $b;',
    'unpack-unpack-value-4-7': b'<?php echo false && [...1.5];echo 1;',
    'unpack-unpack-value-4-8': b'<?php $a=[false && [...1.5]];echo 1;',
    'unpack-unpack-value-5-0': b'<?php $x=NAN;$a=[...$x];echo $a;',
    'unpack-unpack-value-5-1': b'<?php $x=NAN;$a=[1,...$x,2];echo $a;',
    'unpack-unpack-value-5-2': b'<?php $a=[...NAN];echo $a;',
    'unpack-unpack-value-5-3': b'<?php $a=1;$b=[$a,...NAN];echo $b;',
    'unpack-unpack-value-5-4': b'<?php $a=1;$b=[...NAN,$a];echo $b;',
    'unpack-unpack-value-5-5': b'<?php $a=1;$b=[&$a,...NAN];echo $b;',
    'unpack-unpack-value-5-6': b'<?php $a=1;$b=[...NAN,&$a];echo $b;',
    'unpack-unpack-value-5-7': b'<?php echo false && [...NAN];echo 1;',
    'unpack-unpack-value-5-8': b'<?php $a=[false && [...NAN]];echo 1;',
    'unpack-unpack-value-6-0': b'<?php $x="x";$a=[...$x];echo $a;',
    'unpack-unpack-value-6-1': b'<?php $x="x";$a=[1,...$x,2];echo $a;',
    'unpack-unpack-value-6-2': b'<?php $a=[..."x"];echo $a;',
    'unpack-unpack-value-6-3': b'<?php $a=1;$b=[$a,..."x"];echo $b;',
    'unpack-unpack-value-6-4': b'<?php $a=1;$b=[..."x",$a];echo $b;',
    'unpack-unpack-value-6-5': b'<?php $a=1;$b=[&$a,..."x"];echo $b;',
    'unpack-unpack-value-6-6': b'<?php $a=1;$b=[..."x",&$a];echo $b;',
    'unpack-unpack-value-6-7': b'<?php echo false && [..."x"];echo 1;',
    'unpack-unpack-value-6-8': b'<?php $a=[false && [..."x"]];echo 1;',
    'unpack-unpack-value-7-0': b'<?php $x=[];$a=[...$x];echo $a;',
    'unpack-unpack-value-7-1': b'<?php $x=[];$a=[1,...$x,2];echo $a;',
    'unpack-unpack-value-7-2': b'<?php $a=[...[]];echo $a;',
    'unpack-unpack-value-7-3': b'<?php $a=1;$b=[$a,...[]];echo $b;',
    'unpack-unpack-value-7-4': b'<?php $a=1;$b=[...[],$a];echo $b;',
    'unpack-unpack-value-7-5': b'<?php $a=1;$b=[&$a,...[]];echo $b;',
    'unpack-unpack-value-7-6': b'<?php $a=1;$b=[...[],&$a];echo $b;',
    'unpack-unpack-value-7-7': b'<?php echo false && [...[]];echo 1;',
    'unpack-unpack-value-7-8': b'<?php $a=[false && [...[]]];echo 1;',
    'unpack-unpack-value-8-0': b'<?php $x=[1];$a=[...$x];echo $a;',
    'unpack-unpack-value-8-1': b'<?php $x=[1];$a=[1,...$x,2];echo $a;',
    'unpack-unpack-value-8-2': b'<?php $a=[...[1]];echo $a;',
    'unpack-unpack-value-8-3': b'<?php $a=1;$b=[$a,...[1]];echo $b;',
    'unpack-unpack-value-8-4': b'<?php $a=1;$b=[...[1],$a];echo $b;',
    'unpack-unpack-value-8-5': b'<?php $a=1;$b=[&$a,...[1]];echo $b;',
    'unpack-unpack-value-8-6': b'<?php $a=1;$b=[...[1],&$a];echo $b;',
    'unpack-unpack-value-8-7': b'<?php echo false && [...[1]];echo 1;',
    'unpack-unpack-value-8-8': b'<?php $a=[false && [...[1]]];echo 1;',
    'unpack-loop-unpack-0': b'<?php $a=[1];$i=0;while($i++<3){$b=[...$a];$b[0]+=1;echo $a[0],$b[0];}',
    'unpack-loop-unpack-1': b'<?php $x=1;$a=[&$x];$i=0;while($i++<3){$b=[...$a];$b[0]+=1;echo $x,$a[0];}',
    'unpack-loop-unpack-2': b'<?php $x=1;$a=[&$x];unset($x);$i=0;while($i++<3){$b=[...$a];$b[0]+=1;echo $a[0],$b[0];}',
    'unpack-loop-unpack-3': b'<?php $a=[];$a[0]=&$a;$i=0;while($i++<3){$b=[...$a];echo $a===$b;}',
    'unpack-compiler-empty': b'<?php echo [...[]]===[];',
    'unpack-compiler-intkeys': b'<?php echo [...[3=>10,-2=>11],12]===[10,11,12];',
    'unpack-compiler-stringkeys': b'<?php echo [...["k"=>1],"k"=>2,...["j"=>3,"k"=>4]]===["k"=>4,"j"=>3];',
    'unpack-compiler-numericstrings': b'<?php echo [...["0"=>1,"00"=>2]]===[1,"00"=>2];',
    'unpack-compiler-multispread': b'<?php $a=[2=>2];echo [1,...$a,...$a,3]===[1,2,2,3];',
    'unpack-compiler-nested': b'<?php echo [...[...[1],2]]===[1,2];',
    'unpack-compiler-cow': b'<?php $a=[1];$b=[...$a];$a[0]=2;echo $b[0];',
    'unpack-compiler-sharedref': b'<?php $x=1;$a=[&$x];$b=[...$a];$x=2;echo $b[0];',
    'unpack-compiler-singletonref': b'<?php $x=1;$a=[&$x];unset($x);$b=[...$a];$a[0]=2;echo $b[0];',
    'unpack-compiler-sharednested': b'<?php $x=[1];$a=[&$x];$b=[...$a];$x[0]=2;echo $b[0][0];',
    'unpack-compiler-replacementref': b'<?php $x=1;$a=["k"=>&$x];$b=[...$a,...["k"=>2]];$x=3;echo $b["k"];',
    'unpack-compiler-dynamic-read': b'<?php $a=[1];echo [...$a,...($a=[2]),...$a]===[1,2,2];',
    'unpack-compiler-append-overflow': b'<?php echo "before";[9223372036854775807=>1,...[2]];',
    'unpack-compiler-append-overflow-empty': b'<?php echo [9223372036854775807=>1,...[]]===[9223372036854775807=>1];',
    'unpack-compiler-append-overflow-string': b'<?php echo [9223372036854775807=>1,...["k"=>2]]===[9223372036854775807=>1,"k"=>2];',
    'unpack-compiler-scalar-0': b'<?php echo "before";[...null];',
    'unpack-compiler-dynamic-scalar-0': b'<?php $x=null;echo "before";[...$x];',
    'unpack-compiler-scalar-1': b'<?php echo "before";[...true];',
    'unpack-compiler-dynamic-scalar-1': b'<?php $x=true;echo "before";[...$x];',
    'unpack-compiler-scalar-2': b'<?php echo "before";[...false];',
    'unpack-compiler-dynamic-scalar-2': b'<?php $x=false;echo "before";[...$x];',
    'unpack-compiler-scalar-3': b'<?php echo "before";[...1];',
    'unpack-compiler-dynamic-scalar-3': b'<?php $x=1;echo "before";[...$x];',
    'unpack-compiler-scalar-4': b'<?php echo "before";[...1.5];',
    'unpack-compiler-dynamic-scalar-4': b'<?php $x=1.5;echo "before";[...$x];',
    'unpack-compiler-scalar-5': b'<?php echo "before";[..."s"];',
    'unpack-compiler-dynamic-scalar-5': b'<?php $x="s";echo "before";[...$x];',
    'unpack-compiler-scalar-6': b'<?php echo "before";[...NAN];',
    'unpack-compiler-dynamic-scalar-6': b'<?php $x=NAN;echo "before";[...$x];',
    'unpack-compiler-later-dynamic': b'<?php echo "before";[...1,$x];',
    'unpack-compiler-earlier-dynamic': b'<?php echo "before";[$x,...1];',
    'unpack-compiler-later-hole': b'<?php echo "before";[...1,,];',
    'unpack-compiler-earlier-hole': b'<?php echo "before";[,...1];',
    'unpack-compiler-key-warning-first': b'<?php echo "before";[null=>0,...1];',
    'unpack-compiler-key-warning-last': b'<?php echo "before";[...1,null=>0];',
    'unpack-compiler-key-error-first': b'<?php echo "before";[[]=>0,...1];',
    'unpack-compiler-key-error-last': b'<?php echo "before";[...1,[]=>0];',
    'unpack-compiler-nested-scalar': b'<?php echo "before";[...[...1]];',
    'unpack-compiler-skipped-and': b'<?php echo "before";false&&[...1];',
    'unpack-compiler-prepass-selected': b'<?php echo "before";[true?1:[...1]];',
    'unpack-compiler-multiline-scalar': b'<?php echo "before";[1,\n...\n1\n];',
    'unpack-compiler-multiline-dynamic': b'<?php echo "before";[$x,\n...\n1\n];',
}

PREFIX = '''
dec $resume_unpack(pstate, nat) : pstate
def $resume_unpack(S, n) = $drive(S[.COMPLETION = NORMAL], n) -- if S.COMPLETION = BUDGET
def $resume_unpack(S, n) = S -- if S.COMPLETION =/= BUDGET

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
            for name,source in NORMAL_CASES.items():
                source_path=Path(tmp)/f'array-unpack-{len(records):03}.php'
                source_path.write_bytes(source)
                native=subprocess.run([str(types.PHP),'-n',*types.FLAGS,str(source_path)],capture_output=True,env=types.ENV,timeout=10)
                assert native.returncode in (0,255),(name,native.stdout,native.stderr)
                completion='NORMAL'
                if native.returncode==255:
                    match=re.search(rb'Uncaught (Error|TypeError|DivisionByZeroError|ArithmeticError): (.*?) in '+re.escape(str(source_path).encode())+rb':(\d+)',native.stderr);assert match,native.stderr
                    completion='THROWN '+json.dumps(match[1].decode())+' '+byte_sequence(match[2])+' '+match[3].decode()
                parsed=frontend.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
                checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True});assert checked['ok'],checked
                events=[]
                for severity,message,line in re.findall(rb'(Warning|Deprecated): (.*) in .* on line (\d+)',native.stderr):
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
                        'S_out.COMPLETION = '+completion,'S_out.ORIGIN = eps','S_out.HELD = eps',
                        'S_out.POOLS = S.POOLS','S_out.CODE = S.CODE',
                        '$heap_valid($heap_graph(S_out))']
                if name.startswith('loop-'):
                    for budget in range(101):
                        checks += [f'S_budget{budget} = $drive(S, {budget})',
                                   f'$resume_unpack(S_budget{budget}, 10000) = S_out',
                                   f'S_budget{budget}.POOLS = S.POOLS',
                                   f'S_budget{budget}.CODE = S.CODE',
                                   f'$heap_valid($heap_graph(S_budget{budget}))']
                assertions.append(checks)
                records.append({'id':name,'source_base64':base64.b64encode(source).decode(),'ast':checked['ast'],
                                'oracle_exit_status':native.returncode,'oracle_stdout':base64.b64encode(native.stdout).decode(),
                                'oracle_stderr':base64.b64encode(native.stderr).decode()})
            for index,checks in enumerate(assertions):
                fixture=Path(tmp)/'array_unpack.watsup'
                fixture.write_text(PREFIX+'dec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+check+'\n' for check in checks))
                run=subprocess.run([str(runner),*map(str,specs),str(fixture)],capture_output=True,text=True,cwd=ROOT,timeout=120)
                if run.returncode or run.stdout.strip()!='true':
                    (ROOT/'.tools/array_unpack-source-failure.watsup').write_text(fixture.read_text())
                    raise AssertionError((index,run.stdout,run.stderr))
    finally:
        frontend.close();adapter.close()
    assert before==types.syntax_validation.implementation_fingerprint(),'inputs changed during array_unpack gate'
    report={'result':'pass','classification':'checked-source array unpacking, builder ownership, reference transfer and budget resumption',
            'source_cases':len(records),'state_cases':len(assertions),'assertions':sum(map(len,assertions)),
            'records':records,'fingerprint':before}
    (ROOT/'coverage/semantics/array_unpack.json').write_text(json.dumps(report,indent=2)+'\n')
    print({key:report[key] for key in ('result','source_cases','state_cases','assertions')})

if __name__=='__main__':
    main()
