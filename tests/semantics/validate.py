#!/usr/bin/env python3
"""Fresh-process, original-byte differential tests for the checked machine."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests'))
import validate as syntax_validation

PROFILE = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
PHP = ROOT / '.tools/php/bin/php'
ENV = dict(os.environ, LC_ALL='C', TZ='UTC')
ENV.pop('PHP_SPEC_SCRIPT_ENCODING', None)
FLAGS = [flag for key, value in PROFILE.items() for flag in ('-d', key + '=' + value)]
CASES = {
    'empty': b'<?php ;',
    'bytes': b'<?php echo "a\\x00\\xff", "", "BC", "DEF";',
    'integers': b'<?php echo 0, 42, 9223372036854775807;',
    'constants': b'<?php echo true, false, NULL, TrUe, FaLsE;',
    'blocks': b'outside<?php { echo "inside"; { echo 73; } } ?>end',
    'discard': b'<?php "unused"; 72; true; echo "end";',
    'undefined': b'<?php\necho "prefix", UNKNOWN_CONST; echo "unreachable";',
    'static-break': b'<?php echo "unreachable";\nbreak;',
    'numeric-types': b'<?php echo (6/3)===2,":",(5/2)===2.5,":",(6.0/3)===2.0,":",(6.0/3)!==2,":",(PHP_INT_MAX+1)===9223372036854775808.0;',
    'numeric-special-identity': b'<?php echo 0.0===-0.0,":",NAN===NAN,":",NAN!==NAN,":",INF===INF;',
    'scalar-strict-identity': b'<?php echo false===null,":",false!==null,":",1!==true,":","1"!==1,":","a"==="a";',
    'numeric-lines-binary': b'<?php\n$a="2x";\n$b="3x";\necho $a\n+\n$b;',
    'numeric-lines-unary': b'<?php\n$a="2x";\necho -\n$a;',
    'numeric-lines-both-missing': b'<?php\necho $a\n+\n$b;',
    'numeric-lines-unary-missing': b'<?php\necho -\n$a;',
    'numeric-lines-division': b'<?php\necho 1\n/\n0;',
    'numeric-lines-rhs-assignment': b'<?php\necho $missing+($a=\n2);',
    'numeric-basic': b'<?php echo 6/3,":",5/2,":",6.0/3,":",(2+3)*4;',
    'numeric-overflow': b'<?php echo PHP_INT_MAX+1,":",PHP_INT_MIN/-1,":",PHP_INT_MAX*PHP_INT_MAX;',
    'numeric-strings': b'<?php echo "01"+1,":"," 1e2 "+1,":","2tail"+3;',
    'numeric-string-error': b'<?php echo "prefix","x"+1;',
    'numeric-string-order': b'<?php echo "2tail"+"x";',
    'numeric-zero-divisor': b'<?php echo "prefix",1/0;',
    'numeric-unary': b'<?php $a="2tail"; echo -$a,":",+true,":",-0.0,":",+null;',
    'numeric-unary-error': b'<?php $a="x"; echo -$a;',
    'numeric-float-literals': b'<?php echo 1.2345678901234567,":",1e-300,":",5e-324,":",1e309;',
    'numeric-nan-output': b'<?php echo NAN,":",INF,":",-INF;',
    'numeric-nan-variable-name': b'<?php $n=NAN; $$n=1; echo $$n; unset($$n);',
    'numeric-nan-reference-name': b'<?php $n=NAN; $a=&$$n; $a=7; echo $$n;',
    'numeric-delayed-read': b'<?php $a=1;echo $a+($a=2),":",$a;',
    'numeric-captured-read': b'<?php $a=1;$n="a";echo $$n+($a=2),":",$a;',
    'assignment-chain': b'<?php $a=$b=42; echo $a,$b;',
    'assignment-copy': b'<?php $a=1; $b=$a; $a=7; echo $a,$b;',
    'alias-write': b'<?php $a=1; $b=&$a; $c=&$b; $a=7; echo $a,$b,$c;',
    'alias-rebind': b'<?php $a=1; $b=&$a; $c=&$b; $d=2; $b=&$d; $b=3; echo $a,$b,$c,$d;',
    'reference-initialize': b'<?php $a=&$missing; echo $a,$missing; $a=9; echo $missing;',
    'unset-reference': b'<?php $a=1; $b=&$a; unset($a); $a=7; echo $a,$b;',
    'missing-read': b'<?php\necho "before",$missing,"after"; $missing;',
    'dynamic-name': b'<?php $name="a"; $$name=4; $b=&$$name; $name="b"; $$name=7; echo $a,$b;',
    'dynamic-delayed-name': b'<?php $a="unchanged"; $n="a"; $$n=($n="b"); echo $a,$b;',
    'dynamic-captured-name': b'<?php $a="old-a";$b="old-b"; ${($n="a")}=($n="b"); echo $a,$b;',
    'dynamic-unset': b'<?php $name="a"; $a=3; unset($$name); echo $a;',
    'dynamic-numeric-name': b'<?php ${42}=7; ${true}=8; ${null}=9; echo ${42},${true},${null};',
    'dynamic-write-initialize': b'<?php $n="missing"; $$n=$missing; echo $missing;',
    'cv-write-missing': b'<?php $missing=$missing; echo $missing;',
    'discard-variable': b'<?php $missing; ${"missing"}; $name="missing"; $$name;',
    'assignment-source-lines': b'<?php\n$a=\n$missing;\necho\n$missing;\n$n="b";\n$$n=\n$missing;',
    'dynamic-captured-nested': b'<?php $n="a";$a=1;$b="OLD"; ${$$n}=($a="b"); echo $b,${1};',
    'dynamic-ref-rhs-changes-name': b'<?php $n="a"; $$n =& ${($n="b")}; $a="A"; $b="B"; echo $a,$b,$n;',
    'captured-ref-rhs-changes-name': b'<?php ${($n="a")} =& ${($n="b")}; $a="A"; echo $a,$b,$n;',
    'dynamic-nul-name': b'<?php ${"a\\0b"}=3;echo ${"a\\0b"};',
    'dynamic-source-lines': b'<?php\necho ${\n$missing\n};\n${\n$missing\n}=\n$other;\nunset(${\n$missing\n});\n$a=&${\n$missing\n};',
    'dynamic-reference': b'<?php $n="x"; $a=&$$n; $a=7; echo $x;',
    'dynamic-reference-rebind': b'<?php $a=1; $b=2; $n="a"; $$n=&$b; $a=7; echo $a,$b;',

}


CASES.update({
    'element-target-cv-initialize': b'<?php $a[$x]=&$x;echo $a[""]===null;',
    'element-target-dynamic-initialize': b'<?php $n="x";$a[$x]=&$$n;echo $a[""]===null;',
    'element-target-literal-cv-initialize': b'<?php $a[$x]=&${"x"};echo $a[""]===null;',
    'element-target-nested-append': b'<?php $a=[];$a[][0]=&$x;$x=9;echo $a[0][0];',
    'element-target-both-append': b'<?php $a=[];$a[]=&$a[];echo $a[0]===null,$a[1]===null;',
    'element-target-append-self': b'<?php $a=[];$a[]=&$a;echo $a[0]===$a;',
    'element-target-reference-key': b'<?php $x=0;$a=[];$b=[1,2];$a[($n=&$x)]=&$b[($x=1)];$b[1]=9;echo $a[1];',
    'element-target-result-current': b'<?php $x=1;$a=[];echo ($a[0]=&$x)+($x=2);',
    'element-target-result-old-cell': b'<?php $x=1;$y=2;$a=[];echo ($a[0]=&$x)+($x=&$y);',
    'element-target-result-last-owner': b'<?php $a=[];$b=[1];echo ($a[0]=&$b[0])+(($a=[2])[0]+($b=[3])[0]);',
    'element-target-literal-assignment': b'<?php $b=[($a[]=&$x)];$x=9;echo $b[0]===null,$a[0];',
    'element-target-singleton-copy': b'<?php $x=1;$a=[&$x];unset($x);$b=$a;$a[0]=&$b[0];$a[0]=9;echo $a[0],$b[0];',
    'element-target-singleton-unrelated': b'<?php $x=1;$a=[&$x];unset($x);$b=$a;$a[1]=&$b[0];$a[0]=9;echo $a[0],$a[1],$b[0];',
    'element-target-overflow': b'<?php $a=[PHP_INT_MAX=>1];$a[]=&$x;',
    'element-target-nested-overflow': b'<?php $a=[PHP_INT_MAX=>1];$a[][0]=&$x;',
    'element-target-false': b'<?php $a=false;$x=1;$a[0]=&$x;echo $a[0];',
    'element-target-scalar-error': b'<?php $a=1;$a[0]=&$x;',
    'element-target-cv-self-key': b'<?php $a[$a]=&$a;',
    'element-target-same-slot': b'<?php $a=[1];$a[0]=&$a[0];$a[0]=9;echo $a[0];',
    'element-target-unset-old-root': b'<?php $a=[1];$x=2;$a[0]=&$x;unset($x);$b=$a;$b[0]=9;echo $a[0],$b[0];',
    'element-target-multiline-cv': b'<?php\n$a[\n$x\n]=&\n$x;echo $a[""]===null;',
    'element-target-multiline-dynamic': b'<?php\n$n="x";\n$a[\n$x\n]=&\n$$n;echo $a[""]===null;',
    'element-target-nested-alias': b'<?php $x=[1];$a=[&$x];$b=$a;$y=2;$a[0][0]=&$y;$y=9;echo $a[0][0],$b[0][0],$x[0];',
    'element-source-self-append': b'<?php $x=&$x[];echo $x===null;',
    'element-source-singleton-copy': b'<?php $x=1;$a=[&$x];unset($x);$b=$a;$y=&$a[0];$y=9;echo $a[0],$b[0];',
    'element-source-literal-key-order': b'<?php $a=[$k=>&$x[$k]];echo $a[""]===null;',
    'element-source-target-name-order': b'<?php $a=[];${$k}=&$a[$k];echo ${""}===null;',
    'element-source-overflow': b'<?php $a=[PHP_INT_MAX=>1];$x=&$a[];',
    'element-source-false': b'<?php $a=false;$x=&$a[0];echo $x===null;',
    'element-source-scalar-error': b'<?php $a=1;$x=&$a[0];',
    'element-source-nested-copy': b'<?php $a=[[1]];$b=$a;$x=&$a[0][0];$x=9;echo $a[0][0],$b[0][0];',
    'element-source-literal-replaces-container': b'<?php $a=[1];$a=[&$a[0]];$b=$a;$b[0]=9;echo $a[0],$b[0];',
    'element-source-literal-duplicates': b'<?php $a=[1,2];$b=[0=>&$a[0],0=>&$a[1]];$b[0]=9;echo $a[0],$a[1];',
    'element-source-literal-appends': b'<?php $a=[];$b=[&$a[],&$a[]];$b[0]=1;$b[1]=2;echo $a[0],$a[1];',
    'element-source-literal-nested-append-reject': b'<?php echo "unreachable";$b=[&$a[][0]];',
    'element-source-literal-append-lines': b'<?php\n$b=[\n1,\n&$a[]\n];',
    'element-source-literal-key-append-reject': b'<?php\n$b=[\n1,\n&$a[$c[]]\n];',
    'element-source-literal-append-reference-key': b'<?php $a=[];$b=[&$a[($x=&$c[])]];echo $b[0]===null;',
    'element-source-literal-append-reference-value': b'<?php $b=[($x=&$a[])];echo $b[0]===null;',
    'element-source-shared-self': b'<?php $a=[&$a];$x=&$a[0];$x=[7];echo $a[0];',
    'element-source-singleton-self': b'<?php $a=[&$a];$b=$a;unset($a);$x=&$b[0];$x=[7];echo $b[0][0];',
    'element-source-old-cell': b'<?php $a=[1];echo ($x=&$a[0])+($a=[2])[0];',
    'element-source-dynamic-target-replaces-container': b'<?php $a=[1];$n="a";echo ($$n=&$a[0])+($a=2);',
    'element-source-literal-float-target': b'<?php $a=[1];${1.5}=&$a[0];${1.5}=9;echo $a[0];',
    'element-source-multiline': b'<?php\n$x=&\n$a[\n$k\n];echo $x===null;',
    'element-source-nested-false-line': b'<?php\n$a=[false];\n$x=&$a[0][\n0\n];echo $x===null;',
    'reference-cv-timing-string-name': b'<?php ${${"x"}}=&${"x"};echo ${""}===null;',
    'reference-cv-timing-integer-name': b'<?php ${${12}}=&${12};echo ${""}===null;',
    'reference-cv-timing-captured-target': b'<?php $n="x";${$$n}=&$x;echo ${""}===null;',
    'reference-cv-timing-existing-cell': b'<?php $x="x";${($k=&$x)}=&$x;echo $x,$k;',
    'reference-cv-timing-array-name': b'<?php $x=[];${$x}=&$x;echo ${"Array"}===$x;',
    'float-cv-small-name': b'<?php ${5e-324}=1;echo ${5e-324}+(${5e-324}=2);',
    'float-cv-zero-name': b'<?php ${0.0}=1;echo ${0.0}+(${0.0}=2);',
    'float-cv-array-identity': b'<?php ${1.5}=[NAN];echo ${1.5}===(${1.5}=[NAN]);',
    'float-cv-negative-zero-control': b'<?php ${-0.0}=1;echo ${-0.0}+(${-0.0}=2);',
    'array-reference-literal-write': b'<?php $x=1;$a=[&$x];$a[0]=7;echo $x;$x=9;echo $a[0];',
    'array-reference-literal-initialize': b'<?php $a=[&$x];echo $a[0]===null,$x===null;$x=7;echo $a[0];',
    'array-reference-literal-nested-shared': b'<?php $x=[1];$a=[&$x];$b=$a;$b[0][0]=9;echo $x[0],$a[0][0],$b[0][0];',
    'array-reference-literal-nested-singleton': b'<?php $x=[1];$a=[&$x];unset($x);$b=$a;$b[0][0]=9;echo $a[0][0],$b[0][0];',
    'array-reference-literal-value-overwrite': b'<?php $x=1;$a=[0=>&$x,0=>2];$a[0]=9;echo $x,$a[0];',
    'array-reference-literal-ref-overwrite': b'<?php $x=1;$y=2;$a=[0=>&$x,0=>&$y];$a[0]=9;echo $x,$y;',
    'array-reference-literal-unset-entry': b'<?php $x=1;$a=[&$x];unset($a[0]);$a[]=7;echo $x,$a[1];',
    'array-reference-literal-rebind': b'<?php $x=1;$y=2;$a=[&$x];$x=&$y;$a[0]=9;echo $a[0],$x,$y;',
    'array-reference-literal-self': b'<?php $a=[&$a];echo $a[0]===$a;$a[1]=7;echo $a[0][1];',
    'array-reference-literal-self-copy': b'<?php $a=[&$a];$b=$a;unset($a);$c=$b;$c[0]=[7];echo ($b[0]===[7])+0;',
    'array-reference-literal-self-union-left': b'<?php $a=[&$a];$b=$a;unset($a);$c=$b+[1=>2];$c[0]=[7];echo ($b[0]===[7])+0;',
    'array-reference-literal-self-union-right': b'<?php $a=[&$a];$b=$a;unset($a);$c=[1=>2]+$b;$c[0]=[7];echo ($b[0]===[7])+0;',
    'array-reference-literal-dead-cycle': b'<?php $x=1;$a=[&$x];$dead=[&$x,&$dead];unset($x,$dead);$b=$a;$b[]=0;$b[0]=9;echo $a[0],$b[0];',
    'array-reference-literal-dead-acyclic': b'<?php $x=1;$a=[&$x];$dead=[&$x];unset($x,$dead);$b=$a;$b[]=0;$b[0]=9;echo $a[0],$b[0];',
    'array-reference-literal-key-acquires': b'<?php\n$a=[$x=>&$x];echo $a[""]===null;',
    'array-reference-literal-key-missing': b'<?php\n$a=[$x=>&$y];echo $a[""]===null;',
    'array-reference-literal-key-captured': b'<?php\n$n="x";$a=[$$n=>&$x];echo $a[""]===null;',
    'array-reference-literal-key-dynamic': b'<?php $n="x";$a=[$n=>&${$n="y"}];echo $a["y"]===null;',
    'array-reference-literal-key-ref': b'<?php $n="x";$a=[($q=&$n)=>&${$n="y"}];echo $a["y"]===null;',
    'array-reference-literal-key-old-cell': b'<?php $n="x";$m="y";$a=[($q=&$n)=>&${[($n=&$m),($q=&$m),"y"][2]}];$y=7;echo $a["x"];',
    'array-reference-literal-key-order': b'<?php $n="x";$x=1;$y=2;$a=[($n="y")=>&$$n];$a["y"]=9;echo $x,$y;',
    'array-reference-literal-key-lines': b'<?php\n$a=[\n$x\n=>&\n$y\n];echo $a[""]===null;',
    'array-reference-literal-null-key-lines': b'<?php\n$a=[\nnull\n=>&\n$x\n];echo $a[""]===null;',
    'array-reference-literal-overflow': b'<?php\n$a=[PHP_INT_MAX=>&$x,&$y];',
    'array-reference-literal-union-conflict': b'<?php $x=1;$a=[&$x];unset($x);$b=[0=>2]+$a;$b[0]=9;echo $a[0],$b[0];',
})


CASES.update({
    'reference-result-mutated-value': b'<?php $a=1;echo ($x=&$a)+($a=2);',
    'reference-result-mutated-type': b'<?php $a=1;echo ($x=&$a)===($a="1");',
    'reference-result-rebound-name': b'<?php $a=1;$b=2;echo ($x=&$a)+($a=&$b);',
    'reference-result-dynamic-target': b'<?php $n="x";$a=1;echo ($$n=&$a)+($a=2);',
    'reference-result-dynamic-source': b'<?php $n="a";$a=1;echo ($x=&$$n)+($a=2);',
    'reference-result-dynamic-name': b'<?php $n="a";$a=1;$b=2;${($x=&$n)}=($n="b");echo $a,$b;',
    'reference-result-array-key': b'<?php $a=1;$r=[($x=&$a)=>($a=2)];echo $r[2];',
    'reference-result-array-base': b'<?php $a=[1];echo ($x=&$a)[($a=[2])[0]-2];',
    'reference-result-array-rebind': b'<?php $a=[1];$b=[2];echo ($x=&$a)[($a=&$b)[0]-2];',
    'reference-result-nan-identity': b'<?php $a=[NAN];echo ($x=&$a)===($a=[NAN]);',
    'reference-result-literal-copy': b'<?php $a=1;$r=[($x=&$a)];$a=2;echo $r[0];',
    'reference-result-ordinary-copy': b'<?php $a=1;$b=($x=&$a);$a=2;echo $a,$b;',
    'reference-result-old-cell': b'<?php $a=1;$b=2;echo ($x=&$a)+(($a=&$b)+($x=&$b));',
    'reference-result-old-array-cell': b'<?php $a=[1];$b=[2];$c=($x=&$a)+(($a=&$b)+($x=&$b));echo $c[0];',
    'reference-result-null-key': b'<?php $a=1;$r=[($x=&$a)=>($a=null)];echo $r[""]===null;',
    'reference-result-rhs': b'<?php $a=1;$r=[];$r[0]=($x=&$a);$a=2;echo $r[0];',
})


CASES.update({
    'array-nested-key-delayed': b'<?php $a=[[1],[2]];$i=0;echo $a[$i][(($i=1)===1)-1];',
    'array-nested-key-captured': b'<?php $a=[[1],[2]];$i=0;$n="i";echo $a[$$n][(($i=1)===1)-1];',
    'array-nested-root-delayed': b'<?php $a=[[1]];echo $a[0][($a=[[2]])[0][0]-2];',
    'array-nested-root-captured': b'<?php echo ($a=[[1]])[0][($a=[[2]])[0][0]-2];',

    'array-dynamic-base-delayed': b'<?php $a=[1];$n="a";echo $$n[($a=[2])[0]-2];',
    'array-dynamic-base-name-delayed': b'<?php $a=[1];$b=[2];$n="a";echo $$n[(($n="b")==="b")-1];',
    'array-dynamic-base-name-captured': b'<?php $a=[1];$b=[2];$n="a";echo ${($n="a")}[ (($n="b")==="b")-1 ];',
    'array-captured-name-base-delayed': b'<?php $a=[1];$n="a";echo ${($n="a")}[($a=[2])[0]-2];',

    'array-unary-fold-line': b'<?php\necho [\n-\n1,\n2\n];',
    'array-nan-shared-identity': b'<?php $a=[NAN];$b=$a;echo $a===$a,$a===$b;echo [NAN]===[NAN];$b=$a+[];echo $a===$b;',
    'array-nested-fold-line': b'<?php\necho [\n[3][0]-1,\n9\n];',
    'array-basic': b'<?php\n$a=[1,2];echo $a[0],$a[1];',
    'array-identity': b'<?php\necho [1] === [1], [1]!==[1.0], [1,2]!==[1=>2,0=>1], [[1]] === [[1]];',
    'array-union': b'<?php\n$a=[1,2]+[0=>3,2=>4,"x"=>5];echo $a[0],$a[1],$a[2],$a["x"];',
    'array-keydelayed': b'<?php\n$k=0;$a=[$k=>($k=1)];echo $a[1];',
    'array-keycaptured': b'<?php\n$k=0;$n="k";$a=[$$n=>($k=1)];echo $a[0];',
    'array-keymissing': b'<?php\n$a=[$missing=>1];echo $a[""];',
    'array-keydynamicmissing': b'<?php\n$n="missing";$a=[$$n=>1];echo $a[""];',
    'array-keynull': b'<?php\n$a=[null=>1];echo $a[null];',
    'array-floatkey': b'<?php\n$a=[1.5=>1,INF=>2,NAN=>3];echo $a[1],$a[0];',
    'array-negative': b'<?php\n$a=[-5=>1,2,3];echo $a[-5],$a[-4],$a[-3];',
    'array-max': b'<?php\n$a=[PHP_INT_MAX=>1,2];',
    'array-missing': b'<?php\n$a=[];echo $a["a"],$a[1];',
    'array-arrayecho': b'<?php\necho [\n1,\n2\n];',
    'array-arrayechodynamic': b'<?php\n$a=1;echo [\n1,\n$a\n];',
    'array-keyline': b'<?php\n$a=[\nnull=>\n1\n];echo $a[\nnull\n];',
    'array-keyfloatline': b'<?php\n$a=[\n1.5=>\n1\n];',
    'array-nestedline': b'<?php\necho [\n[\n1\n]\n];',
    'array-dimline': b'<?php\n$a=[];echo $a[\n"a"\n];',
    'array-dimdelayed': b'<?php\n$a=[1,2];echo $a[($a=[3,4])[0]-3];',
    'array-missing-nul': b'<?php\n$a=[];echo $a["a\\0b"],$a["a\\nb"];',
    'array-missing-cv-dimension': b'<?php\n$a=[];echo $a[$missing];',
    'array-missing-both': b'<?php\n$a=[$missingkey=>$missingvalue];echo $a[""];',
    'array-key-by-value-copy': b'<?php\n$a=[1,2];$b=$a;$a=[3];echo $b[0],$b[1],$a[0];',
    'array-key-collision-types': b'<?php\n$a=[1=>"a","1"=>"b",true=>"c",1.0=>"d",null=>"e",false=>"f",0=>"g"];echo $a[1],$a[0],$a[""];',
    'array-key-canonical-strings': b'<?php\n$a=["01"=>1,"+1"=>2,"-0"=>3,"1 "=>4,"-1"=>5,"9223372036854775808"=>6];echo $a["01"],$a["+1"],$a["-0"],$a["1 "],$a[-1],$a["9223372036854775808"];',
    'array-key-int-min': b'<?php\n$a=[PHP_INT_MIN=>1,2];echo $a[PHP_INT_MIN],$a[PHP_INT_MIN+1];',
    'array-key-int-max-replace': b'<?php\n$a=[PHP_INT_MAX=>1,PHP_INT_MAX=>2];echo $a[PHP_INT_MAX];',
    'array-array-mixed-operators': b'<?php\necho []===null,":",[]!==false,":",[]===[],":",[]+[1];',
    'array-array-type-error': b'<?php\necho "prefix",[1]-[1];',
    'array-array-scalar-type-error': b'<?php\necho "prefix",1+[1];',
    'array-array-unary-type-error': b'<?php\necho "prefix",-[1];',
    'array-array-name-runtime': b'<?php\n$a=[];$$a=1;echo $$a;',
    'array-array-name-dynamic-literal': b'<?php\n$a=1;${[$a]}=2;echo $Array;',
    'array-array-name-nonfold-key': b'<?php\n${[null=>1]}=2;echo $Array;',
    'array-empty-array-line': b'<?php\necho [\n\n];',
    'array-keyed-array-line': b'<?php\necho [\n"key"=>\n1\n];',
    'array-nested-constant-arithmetic-line': b'<?php\necho [\n[1]+[2],\n3\n];',
    'array-nested-constant-dim-line': b'<?php\necho [\n[1][0],\n3\n];',
    'array-nested-dynamic-array-line': b'<?php\n$x=1;echo [\n[\n$x\n]\n];',
    'array-literal-captured-array': b'<?php\n$a=[1];$n="a";$b=[$$n,($a=[2])];echo $b[0][0],$b[1][0];',
    'array-literal-delayed-array': b'<?php\n$a=[1];$b=[$a,($a=[2])];echo $b[0][0],$b[1][0];',
    'array-dimension-key-mutation': b'<?php\n$a=["x"=>1];$k="x";echo $a[($k="x")];',
    'array-nested-dimension-lookup-line': b'<?php\n$a=[[]];echo $a[\n0\n][\n"missing"\n];',
})

CASES.update({
    'array-write-basic': b'<?php\n$a=[];$a[0]=1;$a["x"]=2;echo $a[0],$a["x"];',
    'array-write-nested': b'<?php\n$a=[];$a[0][1]=2;echo $a[0][1];',
    'array-write-append': b'<?php\n$a[]=1;$a[]=2;echo $a[0],$a[1];',
    'array-write-nestedappend': b'<?php\n$a[][]=1;$a[][]=2;echo $a[0][0],$a[1][0];',
    'array-write-copy': b'<?php\n$a=[1];$b=$a;$a[0]=2;echo $a[0],$b[0];',
    'array-write-nestedcopy': b'<?php\n$a=[[1]];$b=$a;$a[0][0]=2;echo $a[0][0],$b[0][0];',
    'array-write-rootrefs': b'<?php\n$a=[1];$b=&$a;$c=$a;$b[0]=2;echo $a[0],$b[0],$c[0];',
    'array-write-nestedrootrefs': b'<?php\n$a=[[1]];$b=&$a;$c=$a;$b[0][0]=2;echo $a[0][0],$b[0][0],$c[0][0];',
    'array-write-false': b'<?php\n$a=false;$a[0]=1;echo $a[0];',
    'array-write-falseinner': b'<?php\n$a=[false];$a[0][0]=1;echo $a[0][0];',
    'array-write-null': b'<?php\n$a=null;$a[0]=1;echo $a[0];',
    'array-write-nullkey': b'<?php\n$a[null]=1;echo $a[""];',
    'array-write-floatkey': b'<?php\n$a[1.5]=1;echo $a[1];',
    'array-write-keyerror': b'<?php\n$a[[]]=1;',
    'array-write-scalarerror': b'<?php\n$a=true;$a[$missing]=$value;',
    'array-write-keyrhswarnings': b'<?php\n$a[$missing]=$value;',
    'array-write-appendrhswarning': b'<?php\n$a[]=$missing;echo $a[0];',
    'array-write-overflowrhswarning': b'<?php\n$a=[PHP_INT_MAX=>1];$a[]=$missing;',
    'array-write-negativehistory': b'<?php\n$a=[-5=>1];$a[]=2;echo $a[-5],$a[-4];',
    'array-write-selfmissing': b'<?php\n$a[0]=$a;echo $a[0]===null;',
    'array-write-selfappendmissing': b'<?php\n$a[]=$a;echo $a[0]===null;',
    'array-write-selfexisting': b'<?php\n$a=[];$a[0]=$a;echo $a[0]===[];',
    'array-write-selfappendexisting': b'<?php\n$a=[];$a[]=$a;echo $a[0]===[];',
    'array-write-aliasself': b'<?php\n$a=[];$b=&$a;$a[0]=$b;echo $a===$a[0];',
    'array-write-dynamicself': b'<?php\n$a=[];$n="a";$$n[0]=$a;echo $a===$a[0];',
    'array-write-cycliccomparison': b'<?php\n$a=[];$b=&$a;$a[0]=$b;$c=[];$d=&$c;$c[0]=$d;echo $a===$c;',
    'array-write-cyclelength': b'<?php\n$a=[];$b=&$a;$a[0]=$b;$c=[];$d=&$c;$c[0]=$d;$c[1]=1;echo $a===$c;',
    'array-write-cyclemutation': b'<?php\n$a=[];$b=&$a;$a[0]=$b;$a[1]=2;echo $a[0]===$a,$a[0]===$a[0][0];',
    'array-write-keydelayed': b'<?php\n$a=[];$i=0;$a[$i]=($i=1);echo $a[1];',
    'array-write-keycaptured': b'<?php\n$a=[];$i=0;$n="i";$a[$$n]=($i=1);echo $a[0];',
    'array-write-rootchanged': b'<?php\n$a=[1];$a[0]=($a=[2]);echo $a[0][0];',
    'array-write-linewrite': b'<?php\n$a[\nnull\n]=\n$missing;',
    'array-write-lineself': b'<?php\n$a[\n0\n]=\n$a;',
    'array-write-linefalse': b'<?php\n$a=false;$a[\n0\n]=\n1;',
    'array-write-lineechoassignment': b'<?php\necho ($a[\n0\n]=\n[]);',
    'array-write-nestedkeyeffects': b'<?php\n$a=[];$i=0;$a[$i][(($i=1)===1)-1]=2;echo $a[1][0];',
    'array-write-nestedrhseffects': b'<?php\n$a=[];$i=0;$a[$i][0]=($i=1);echo $a[1][0];',
})

CASES.update({
    'array-write-review-cycle-write-after': b'<?php\n$a=[];$b=&$a;$a[0]=$b;$a[1]=1;echo $a[0]===$a, $a[0][0]===$a[0];',
    'array-write-review-cycle-nested-write': b'<?php\n$a=[];$b=&$a;$a[0]=$b;$a[0][1]=1;echo $a[0][0]===$a[0],$a[0][1];',
    'array-write-review-cycle-count-shortcircuit': b'<?php\n$a=[];$b=&$a;$a[0]=$b;$c=[];$d=&$c;$c[0]=$d;$c[1]=1;echo $a===$c;',
    'array-write-review-cycle-key-shortcircuit': b'<?php\n$a=[];$b=&$a;$a[0]=$b;$c=[];$d=&$c;$c[1]=$d;echo $a===$c;',
    'array-write-review-self-key-aliases-root': b'<?php\n$a=[1];$b=[2];$a[($a=&$b)[0]]=$a;echo $a[0],$a[2][0],$b[2][0];',
    'array-write-review-nested-rhs-assign-root': b'<?php\n$a=[[1]];$a[0][0]=($a=[[2]]);echo $a[0][0][0][0];',
    'array-write-review-nan-nested-identical-overwrite': b'<?php\n$x=[NAN];$a=[$x];$b=$a;$a[0]=$x;echo $a===$b;',
    'array-write-review-key-error-rhs-throw': b'<?php\n$a=[];$a[[]]=1/0;',
})

CASES.update({
    'array-unset-absent-direct': b'<?php\nunset($a[0]);echo 1;',
    'array-unset-absent-dynamic': b'<?php\n$n="a";unset($$n[0]);echo 1;',
    'array-unset-absent-nested': b'<?php\nunset($a[0][0]);echo 1;',
    'array-unset-absent-dynamic-nested': b'<?php\n$n="a";unset($$n[0][0]);echo 1;',
    'array-unset-absent-key-expr': b'<?php\nunset($a[$k]);echo 1;',
    'array-unset-null-terminal': b'<?php\n$a=[""=>1];unset($a[null]);echo $a===[];',
    'array-unset-null-intermediate': b'<?php\n$a=[""=>[1]];unset($a[null][0]);echo $a[""]===[];',
    'array-unset-false-base': b'<?php\n$a=false;unset($a[0]);echo $a===false;',
    'array-unset-int-base': b'<?php\n$a=1;unset($a[0]);echo $a;',
    'array-unset-string-base': b'<?php\n$a="abc";unset($a[0]);echo $a;',
    'array-unset-key-illegal': b'<?php\n$a=[];unset($a[[]]);echo 1;',
    'array-unset-key-illegal-no-base': b'<?php\nunset($a[[]]);echo 1;',
    'array-unset-key-illegal-null-base': b'<?php\n$a=null;unset($a[[]]);echo 1;',
    'array-unset-key-illegal-int-base': b'<?php\n$a=1;unset($a[[]]);echo 1;',
    'array-unset-missing-key-cow': b'<?php\n$a=[NAN];$b=$a;unset($a[99]);echo $a===$b;',
    'array-unset-missing-nested-key-cow': b'<?php\n$x=[NAN];$a=[$x];$b=$a;unset($a[0][99]);echo $a===$b,$a[0]===$x;',
    'array-unset-missing-parent-key-cow': b'<?php\n$a=[NAN];$b=$a;unset($a[99][0]);echo $a===$b;',
    'array-unset-empty-terminal-cow': b'<?php\n$a=[];$b=$a;unset($a[99]);echo $a===$b;',
    'array-unset-history-positive': b'<?php\n$a=[5=>1];unset($a[5]);$a[]=2;echo $a[6];',
    'array-unset-history-negative': b'<?php\n$a=[-5=>1];unset($a[-5]);$a[]=2;echo $a[-4];',
    'array-unset-history-max': b'<?php\n$a=[PHP_INT_MAX=>1];unset($a[PHP_INT_MAX]);$a[]=2;echo $a[PHP_INT_MAX];',
    'array-unset-delayed-key': b'<?php\n$a=[0=>1,1=>2];$i=0;unset($a[$i+($i=1)]);echo $a[0];',
    'array-unset-delayed-root': b'<?php\n$a=[1];unset($a[($a=[2])[0]-2]);echo $a===[];',
    'array-unset-delayed-name': b'<?php\n$a=[1];$b=[2];$n="a";unset($$n[(($n="b")==="b")-1]);echo $a[0],$b===[];',
    'array-unset-captured-name': b'<?php\n$a=[1];$b=[2];$n="a";unset(${($n="a")}[ (($n="b")==="b")-1]);echo $a===[],$b[0];',
    'array-unset-cycle-unset-self': b'<?php\n$a=[];$b=&$a;$a[0]=$b;unset($a[0]);echo $a===[],$b===[];',
    'array-unset-cycle-unset-nested': b'<?php\n$a=[];$b=&$a;$a[0]=$b;unset($a[0][0]);echo $a[0]===[];',
    'array-unset-empty-read': b'<?php\necho "before";$a[];',
    'array-unset-empty-nested-read': b'<?php\necho "before";$a[][0];',
    'array-unset-empty-unset': b'<?php\necho "before";unset($a[]);',
    'array-unset-empty-nested-unset': b'<?php\necho "before";unset($a[][0]);',
    'array-unset-empty-read-line': b'<?php\necho "before";\necho $a\n[\n];',
    'array-unset-empty-unset-line': b'<?php\necho "before";\nunset($a\n[\n]);',
    'array-unset-false-terminal-key-order': b'<?php\n$a=false;unset($a[$missing]);',
    'array-unset-false-intermediate-key-order': b'<?php\n$a=false;unset($a[$missing][0]);',
    'array-unset-scalar-terminal-key-order': b'<?php\n$a=1;unset($a[$missing]);',
    'array-unset-scalar-intermediate-key-order': b'<?php\n$a=1;unset($a[$missing][0]);',
    'array-unset-null-terminal-key-order': b'<?php\n$a=null;unset($a[$missing]);',
    'array-unset-null-intermediate-key-order': b'<?php\n$a=null;unset($a[$missing][0]);',
    'array-unset-float-key': b'<?php\n$a=[0=>1,1=>2];unset($a[1.5],$a[NAN]);echo $a===[];',
    'array-unset-missing-cv-key': b'<?php\n$a=[""=>1];unset($a[$missing]);echo $a===[];',
    'array-unset-missing-cv-key-intermediate': b'<?php\n$a=[""=>[1]];unset($a[$missing][0]);echo $a[""]===[];',
    'array-unset-array-key-intermediate': b'<?php\n$a=[];unset($a[[]][0]);',
    'array-unset-nested-null-line': b'<?php\n$a=[""=>[]];unset($a[\nnull\n][\n0\n]);',
    'array-unset-absent-nested-line': b'<?php\nunset($a[\n0\n][\n1\n]);',
    'array-unset-root-alias': b'<?php\n$a=[1];$b=&$a;$c=$a;unset($b[0]);echo $a===[],$b===[],$c[0];',
    'array-unset-nested-root-alias': b'<?php\n$a=[[1]];$b=&$a;$c=$a;unset($b[0][0]);echo $a[0]===[],$b[0]===[],$c[0][0];',
    'array-unset-history-overflow-after-reuse': b'<?php\n$a=[PHP_INT_MAX=>1];unset($a[PHP_INT_MAX]);$a[]=2;$a[]=3;',
    'array-unset-history-copy': b'<?php\n$a=[5=>1];unset($a[5]);$b=$a;$a[]=2;$b[]=3;echo $a[6],$b[6];',
    'array-unset-byte-key': b'<?php\n$a=["a\\0b"=>1,"a"=>2];unset($a["a\\0b"]);echo $a===["a"=>2];',
    'array-unset-order-reinsert': b'<?php\n$a=["a"=>1,"b"=>2];unset($a["a"]);$a["a"]=3;echo $a===["b"=>2,"a"=>3];',
})

CASES.update({
    'array-unset-review-multiline-false-intermediate': b'<?php\n$a=false;unset(\n$a\n[$missing]\n[0]\n);',
    'array-unset-review-multiline-dynamic-float': b'<?php\n$n=NAN;unset(\n$$n\n[$missing]\n);',
    'array-unset-review-multiple-unset-name-change': b'<?php\n$a=[1];$b=[2];$n="a";unset($$n[0],${($n="b")}[0]);echo $a===[],$b===[];',
    'array-unset-review-unset-key-rebind-root': b'<?php\n$a=[1];$b=[2];unset($a[($a=&$b)[0]-2]);echo $a===[],$b===[];',
})

CASES.update({
    'profile-local-session-read': b'<?php echo $_SESSION;',
    'profile-local-session-references': b'<?php $n="_SESSION";$$n=1;$b=&$_SESSION;$b=2;echo $_SESSION;unset($_SESSION);echo $b;',
    'profile-local-session-array': b'<?php $_SESSION[]=1;$_SESSION[]=2;$a=$_SESSION;unset($_SESSION[0]);echo $a[0],$_SESSION[1];',
    'profile-local-session-unset': b'<?php unset($_SESSION);unset($_SESSION[0]);',
    'profile-local-http-response-header-read': b'<?php $n="http_response_header";echo $$n;',
    'profile-local-http-response-header-references': b'<?php $n="http_response_header";$$n=1;$b=&$http_response_header;$b=2;echo $$n;unset($http_response_header);echo $b;',
    'profile-local-http-response-header-array': b'<?php $http_response_header[]=1;$http_response_header[]=2;$n="http_response_header";$a=$$n;unset($http_response_header[0]);echo $a[0],$$n[1];',
    'profile-local-http-response-header-unset': b'<?php unset($http_response_header);unset($http_response_header[0]);',
})

# Independent review-authored witnesses keep their original provenance.
CASES.update({
    'string-compiler-line-quoted': b'<?php $u=1;\necho [\n$u,\n"a\nb"\n];',
    'string-compiler-line-heredoc': b'<?php $u=1;\necho [\n$u,\n<<<TXT\na\nb\nTXT\n];',
    'string-compiler-line-nowdoc': b"<?php $u=1;\necho [\n$u,\n<<<'TXT'\na\nb\nTXT\n];",
    'string-compiler-line-empty-heredoc': b'<?php $u=1;\necho [\n$u,\n<<<TXT\nTXT\n];',
    'string-compiler-line-empty-nowdoc': b"<?php $u=1;\necho [\n$u,\n<<<'TXT'\nTXT\n];",
    'string-compiler-line-indented-heredoc': b'<?php $u=1;\necho [\n$u,\n<<<TXT\n  a\n  b\n  TXT\n];',
    'string-compiler-line-empty-content-line': b'<?php $u=1;\necho [\n$u,\n<<<TXT\n\nTXT\n];',
    'string-compiler-line-crlf': b'<?php $u=1;\necho [\n$u,\n<<<TXT\r\na\r\nb\r\nTXT\n];',
    'string-compiler-line-binary-heredoc': b'<?php $u=1;\necho [\n$u,\nb<<<TXT\na\nTXT\n];',
    'string-compiler-line-single-quoted': b"<?php $u=1;\necho [\n$u,\n'a\nb'\n];",
    'string-compiler-line-indented-nowdoc': b"<?php $u=1;\necho [\n$u,\n<<<'TXT'\n    a\n    TXT\n];",
    'string-compiler-line-crlf-empty-nowdoc': b"<?php $u=1;\necho [\n$u,\n<<<'TXT'\r\nTXT\n];",
})


# Ordered compiler activation: exact new source admissions and failure ordering.
CASES.update({
    'compiler-byte-import-conflict': b'<?php use A\\B as \xff; echo 1; use C\\D as \xff;',
    'compiler-multiline-warning-fatal': b'<?php\nuse A;\necho 1;\nuse A;',
    'compiler-array-key-static': b'<?php $a=[[]=>1];',
    'compiler-error-suppresses-output': b'<?php echo "before"; $a=[[]=>1];',
    'compiler-error-before-runtime-undefined': b'<?php echo $missing; $a=[&$x[]];',
    'compiler-warning-before-static-error': b'<?php use A; echo "before"; $a=[[]=>1]; use B;',
    'compiler-import-conflict-after-work': b'<?php echo "before"; use A; use A;',
    'compiler-namespace-work': b'<?php namespace N; echo 1; {echo 2;} namespace M; echo 3;',
    'compiler-bracketed-namespace-work': b'<?php namespace N {echo 1;} namespace M {echo 2;}',
    'compiler-import-warning-work': b'<?php use A; echo 1; use B; echo 2;',
    'compiler-qualified-import-work': b'<?php use A\\B; echo 1;',
    'compiler-folded-string-array': b'<?php $a=["abc"["1x"]]; echo $a[0];',
    'compiler-folded-string-partial-array': b'<?php $u=7;$a=[$u,"abc"["1x"]];echo $a[0],$a[1];',
    'compiler-folded-string-reference-array': b'<?php $u=7;$a=[&$u,"abc"["1x"]];$u=8;echo $a[0],$a[1];',
    'compiler-folded-string-under-assignment': b'<?php $a=[($u=["abc"["1x"]])];echo $a[0][0],$u[0];',
    'compiler-pool-copy-first-mutation': b'<?php $a=[[NAN]];$b=$a;$a[0][0]=1;echo $b[0][0]===NAN,$a[0][0],$a===$b;',
    'compiler-pool-distinct-nan-occurrences': b'<?php $a=[[NAN],[NAN]];echo $a[0]===$a[0],$a[0]===$a[1];',
})

CASES.update({
    'compiler-unmatched-prefix-control': b'<?php use Vendor\\Package as A;echo B\\Missing;',
    'compiler-unqualified-control': b'<?php use Vendor\\Package as A;echo Missing;',
})
COMPILER_ALIAS_RESOLVED = [
    b'<?php use Vendor\\Package as A;echo A\\Missing;',
    b'<?php use Vendor\\Package as Alias;echo aLiAs\\Missing;',
    b'<?php echo "before";use Vendor\\Package as A;echo A\\Missing;',
    b'<?php use Vendor\\Package as A;$u=1;$a=[$u,A\\Missing];',
]

# Retain the original imported-class-prefix discrepancies as exact source cases.
CASES.update({f'namespace-alias-resolved-{i}': source for i, source in enumerate(COMPILER_ALIAS_RESOLVED)})
from namespace_constants import CASES as NAMESPACE_CASES
CASES.update(NAMESPACE_CASES)
CASES['namespace-alias-fully-qualified'] = b'<?php use Vendor\\Package as A;echo \\A\\Missing;'

# Existing compiler emission-line witnesses, now exercised through source execution.
CASES.update({
    'dimension-read-emission-00': b'<?php $u=7;\necho [$u, "abc"[\n"1x"]];',
    'dimension-read-emission-01': b'<?php $u=7;\necho "abc"[\n"1x"];',
    'dimension-read-emission-02': b'<?php $u=7;\necho ["abc"[\n"-1x"]];',
    'dimension-read-emission-03': b'<?php $u=7;\necho [$u=["abc"[\n"1x"]]];',
    'dimension-read-emission-04': b'<?php $u=[NAN];\necho ($u[\n0]=$u);',
    'dimension-read-emission-05': b'<?php $u=1;\necho [\n $u,\n "abc"[\n "1x"\n ],\n];',
    'dimension-read-emission-06': b'<?php $u=1;\necho [\n 1,\n $u,\n "abc"["1x"]\n];',
    'dimension-read-emission-07': b'<?php $u=1;\necho [\n $u,\n NAN\n];',
    'dimension-read-emission-08': b'<?php $u=1;\necho [\n $u,\n true\n];',
    'dimension-read-emission-09': b'<?php $u=1;\necho [\n $u,\n 1+\n 2\n];',
    'dimension-read-emission-10': b'<?php $u=1;\necho [\n $u,\n -\n 2\n];',
    'dimension-read-emission-11': b'<?php $u=1;\necho [\n "abc"[\n "1x"\n]\n];',
    'dimension-read-emission-12': b'<?php $u=1;\necho [\n $u,\n "last"\n];',
    'dimension-read-emission-13': b'<?php $u=1;\necho [\n $u,\n $u+\n 2\n];',
    'dimension-read-emission-14': b'<?php $u=1;\necho [\n $u,\n ($v="abc"[\n "1x"\n ])\n];',
})

# Original-source string write ownership and diagnostic-order regressions.
CASES.update({
    "string-write-regression-00": b'<?php $s="abc";$t=$s;$s[1]="Z";echo $s,":",$t;',
    "string-write-regression-01": b'<?php $a=["abc"];$b=$a;$a[0][1]="Z";echo $a[0],":",$b[0];',
    "string-write-regression-02": b'<?php $x="abc";$a=[&$x];$b=$a;$a[0][1]="Z";echo $x,":",$a[0],":",$b[0];',
    "string-write-regression-03": b'<?php $k=0;$s="abc";$s[$k]=($k=1);echo $s;',
    "string-write-regression-04": b'<?php $a=["abc"];$a[0][0]=($a=["xyz"]);echo $a[0];',
    "string-write-regression-05": b'<?php $n="a";$a="abc";$b="xyz";$$n[0]=($n="b");echo $a,":",$b;',
    "string-write-regression-06": b'<?php $s="abc";$s[0]=$s;echo $s;',
    "string-write-regression-07": b'<?php $a=["abc"];$a[0][0]=$a[0];echo $a[0];',
    "string-write-regression-08": b'<?php $s="abc";$s[0]=&$missing;',
    "string-write-regression-09": b'<?php $s="abc";$r=&$s[0][0];',
    "string-write-regression-10": b'<?php $s="abc";$s[[]]=$missing;',
    "string-write-regression-11": b'<?php $s="abc";$s[[]]=1/0;',
    "string-write-regression-12": b'<?php $s="abc";$s[]=[7];',
    "string-write-regression-13": b'<?php $s="abc";$s[-4]=($u=[7]);echo $u;',
    "string-write-regression-14": b'<?php $s="abc";\n$s[\nnull\n]="";',
    "string-write-regression-15": b'<?php $s="abc";\n$s[\n0\n]=$missing;',
    "string-write-regression-16": b'<?php $s="abc";\n$r=&$s[\nnull\n];',
    "string-write-regression-17": b'<?php $s="abc";\n$s[\nnull\n][0]=7;',
    "string-write-regression-18": b'<?php $s="abc";$s[-1]="\x00Q";echo $s;',
    "string-write-regression-19": b'<?php $s="abc";$x=&$s;$x[1]="Y";echo $s;',
    "string-write-reference-admission": b'<?php $a="abc";$x=&$a[0];',
})

# Retained original-source bare-break diagnostic line discrepancies and controls.
CASES.update({
    'compiler-break-line-same-line': b'<?php break;',
    'compiler-break-line-newline': b'<?php break\n;',
    'compiler-break-line-blank-line': b'<?php break\n\n;',
    'compiler-break-line-comment': b'<?php break /* one\ntwo */;',
    'compiler-break-line-crlf': b'<?php break\r\n;',
    'compiler-break-line-preceding-output': b'<?php echo "hidden";break\n;',
    'compiler-break-line-block': b'<?php {break\n;}',
    'compiler-break-line-leading-newline': b'<?php\nbreak;',
})

# Retained closing-tag terminator-line failures and comment controls.
CASES.update({
    'compiler-break-terminator-closing-tag': b'<?php break ?>\na',
    'compiler-break-terminator-comment-closing-tag': b'<?php break /*x*/ ?>\n',
    'compiler-break-terminator-hash-comment': b'<?php break #a\n;',
    'compiler-break-terminator-slash-crlf': b'<?php break //a\r\n;',
    'compiler-break-terminator-trailing-newline': b'<?php break;\n',
    'compiler-break-terminator-trailing-comment': b'<?php break\n; /*\n*/',
})

# Known temporary write/unset targets reject before their children are compiled.
CASES.update({
    'compiler-temporary-literal-string-target-error': b'<?php "abc"[0]="X";',
    'compiler-temporary-literal-target-rhs-order': b'<?php "abc"[0]=[&$x[]];',
    'compiler-temporary-literal-target-key-not-compiled': b'<?php "abc"[[&$x[]]]="X";',
    'compiler-temporary-literal-target-read-error-not-run': b'<?php (1/0)[0]="X";',
    'compiler-temporary-literal-target-before-runtime': b'<?php echo "before"; "abc"[0]="X";',
    'compiler-temporary-literal-target-unset': b'<?php unset("abc"[0]);',
    'compiler-temporary-literal-target-reference': b'<?php "abc"[0]=&$x;',
    'compiler-temporary-literal-source-reference': b'<?php $x=&"abc"[0];',
    'compiler-temporary-literal-array-target': b'<?php [1][0]="X";',
    'compiler-temporary-literal-array-target-prepass': b'<?php [&$x[]][0]="X";',
    'compiler-temporary-literal-int-target': b'<?php (1)[0]="X";',
    'compiler-temporary-literal-float-target': b'<?php (1.5)[0]="X";',
    'compiler-temporary-literal-const-target': b'<?php NAN[0]="X";',
    'compiler-temporary-literal-assignment-target': b'<?php ($a=[])[0]="X";',
    'compiler-temporary-literal-ref-assignment-target': b'<?php ($a=&$b)[0]="X";',
    'compiler-temporary-literal-unary-target': b'<?php (-1)[0]="X";',
    'compiler-temporary-literal-multiline-target': b'<?php (1\n+2)[\n0]="X";',
    'compiler-temporary-literal-string-multiline-target': b'<?php "abc"[\n0]="X";',
    'compiler-temporary-literal-nowdoc-target': b"<?php (<<<'T'\nabc\nT\n)[0]='X';",
    'compiler-temporary-literal-read-control': b'<?php echo "abc"[0];',
    'compiler-temporary-literal-array-read-control': b'<?php echo [1][0];',
    'compiler-temporary-variable-target-control': b'<?php $x="abc"; $x[0]="X"; echo $x;',
})

CONFORMANCE = ['reference-rebind', 'reference-assignment-result', 'dynamic-variable', 'delayed-read', 'array-alias-self-cycle', 'array-captured-lhs-key', 'array-captured-lhs-name', 'array-delayed-lhs-key', 'array-delayed-lhs-name', 'array-distinct-cycle-comparison', 'array-dynamic-self-cycle', 'array-nested-self-index', 'array-rhs-overwrites-root', 'array-self-append', 'array-self-index', 'array-self-key-side-effect']
CONFORMANCE += ['array-reference-copy', 'array-singleton-reference-copy', 'array-late-singleton-reference',
                'array-duplicate-reference-copy', 'array-union-left-singleton', 'array-union-right-singleton',
                'array-reference-key-acquisition', 'array-reference-delayed-key']
CONFORMANCE += ['reference-cv-source-initialization', 'reference-cv-source-multiline',
                'reference-dynamic-target-initialization', 'reference-dynamic-source-initialization',
                'float-variable-name-delayed', 'overflow-float-variable-name-delayed',
                'negative-float-variable-name-captured', 'boolean-variable-name-captured',
                'reference-float-cv-initialization']
CONFORMANCE += ['element-reference-source-copy', 'element-reference-source-append',
                'element-reference-source-nested-missing', 'element-reference-literal-copy',
                'element-reference-dynamic-name', 'element-reference-source-container-rebind',
                'element-reference-source-existing-wrapper']
CONFORMANCE += ['element-reference-target-copy', 'element-reference-target-rebind',
                'element-reference-target-self-cycle', 'element-reference-target-same-array',
                'element-reference-target-append', 'element-reference-target-key-replaces-root',
                'element-reference-target-source-replaces-root', 'element-reference-target-self-key',
                'element-reference-target-before-cv', 'array-reference-append-prepass',
                'array-reference-nested-append-prepass', 'array-reference-assignment-key-prepass',
                'array-reference-after-copy', 'array-union-left-self-reference',
                'array-union-right-self-reference']
CONFORMANCE += ['numeric-min-trailing-space', 'numeric-min-nul-control',
                'numeric-min-leading-zero-space', 'numeric-min-incomplete-exponent-control',
                'numeric-positive-overflow-incomplete-exponent',
                'numeric-negative-overflow-incomplete-exponent',
                'numeric-incomplete-exponent-overflow-control']
CONFORMANCE += ['string-read-dynamic-literal-prepass']
CONFORMANCE += ['scalar-read-ignores-key-coercion', 'scalar-read-undefined-order', 'string-read-array-key-error', 'string-read-assignment-prepass-barrier', 'string-read-delayed-base', 'string-read-float-casts', 'string-read-float-text-error', 'string-read-literal-prepass', 'string-read-missing-key', 'string-read-negative-bounds', 'string-read-negative-literal-prepass', 'string-read-null-bool-casts', 'string-read-numeric-keys', 'string-read-reference-key', 'string-read-trailing-key']
CONFORMANCE += ['string-write-array-rhs-order', 'string-write-negative-before-rhs', 'string-write-append-before-rhs', 'string-write-empty-after-key', 'string-write-extension-result', 'string-write-key-warning-before-bound', 'string-reference-key-before-error', 'string-nested-key-before-error']
for identifier in CONFORMANCE:
    CASES['conformance-' + identifier] = (ROOT / 'tests/semantics/conformance' / (identifier + '.php')).read_bytes()

# Deterministic alias interactions vary mutations rather than mirroring rules.
rng = random.Random(85010)
for number in range(20):
    statements = ['<?php', '$a=1;', '$b=2;', '$c=3;']
    for _ in range(20):
        left, right = rng.choice('abc'), rng.choice('abc')
        operation = rng.randrange(5)
        if operation == 0:
            statements.append(f'${left}={rng.randrange(10)};')
        elif operation == 1:
            statements.append(f'${left}=&${right};')
        elif operation == 2:
            statements.append(f'${left}=${right};')
        elif operation == 3:
            statements.append(f'unset(${left});')
        else:
            statements.append(f'$n="{left}"; $$n=${right};')
        statements.append('echo $a,$b,$c,";";')
    CASES[f'generated-alias-{number:02}'] = '\n'.join(statements).encode()


# Review-authored scalar cross-product seed, independent of evaluator clauses.
scalar_values = ['null', 'false', 'true', '0', '-1', 'PHP_INT_MAX', 'PHP_INT_MIN',
                 '0.0', '-0.0', '1.5', 'INF', 'NAN', '""', '"x"', '"2tail"', '" 3 "', '"1e999"']
rng = random.Random(6614)
for number in range(80):
    left, right = rng.choice(scalar_values), rng.choice(scalar_values)
    operator = rng.choice(['+', '-', '*', '/', '===', '!=='])
    CASES[f'generated-scalar-{number:02}'] = f'<?php\n$a={left};$b={right};echo $a {operator} $b;'.encode()


# Independent reviewer key-collision seed exercises canonicalization and ordering.
array_keys = ['0', '-1', '1.2', 'null', 'true', 'false', '"1"', '"01"',
              '"+1"', '"-0"', 'PHP_INT_MIN', 'PHP_INT_MAX']
rng = random.Random(7116)
for number in range(40):
    first, second, third = [rng.choice(array_keys) for _ in range(3)]
    CASES[f'generated-array-keys-{number:02}'] = (
        f'<?php\n$a=[{first}=>1,{second}=>2,{third}=>3];'
        f'echo $a[{first}],$a[{second}],$a[{third}];').encode()


def fingerprint():
    return syntax_validation.implementation_fingerprint()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', default='', help='Run source cases with this ID prefix; always retain outcome negatives.')
    args = parser.parse_args()
    selected = {name: source for name, source in CASES.items() if name.startswith(args.prefix)}
    assert selected, 'no source cases matched prefix'
    before = fingerprint()
    results = []
    negatives = []
    with tempfile.TemporaryDirectory(prefix='php-semantics-') as directory:
        for name, source in selected.items():
            path = Path(directory) / (name + '.php')
            path.write_bytes(source)
            semantic = subprocess.run([str(ROOT / 'bin/php-semantics'), str(path)],
                                      capture_output=True, env=ENV, timeout=35, cwd=directory)
            actual = json.loads(semantic.stdout)
            oracle = subprocess.run([str(PHP), '-n', *FLAGS, str(path)], cwd=directory,
                                    capture_output=True, env=ENV, timeout=30)
            expected = {'stdout': base64.b64encode(oracle.stdout).decode(),
                        'stderr': base64.b64encode(oracle.stderr).decode(),
                        'exit_status': oracle.returncode}
            assert semantic.returncode == 0, (name, actual)
            assert actual['status'] in {'normal', 'php_error', 'static_rejection'}, (name, actual)
            assert all(actual[k] == v for k, v in expected.items()), (name, actual, expected)
            results.append({'id': name, 'source_sha256': hashlib.sha256(source).hexdigest(),
                            'source_base64': base64.b64encode(source).decode(),
                            'context': {'file': str(path), 'cwd': directory},
                            'provenance': ('tests/semantics/conformance/' + name.removeprefix('conformance-') + '.php') if name.startswith('conformance-') else 'authored/generated in tests/semantics/validate.py',
                            'semantic': actual, 'oracle': expected, 'comparison': 'pass'})
        path = Path(directory) / 'unsupported.php'
        path.write_bytes(b'<?php strlen("a");')
        result = subprocess.run([str(ROOT / 'bin/php-semantics'), str(path)], capture_output=True, env=ENV, timeout=35, cwd=directory)
        negatives.append({"source": base64.b64encode(path.read_bytes()).decode(), "command": result.args,
                          "exit_status": result.returncode, "observation": json.loads(result.stdout)})
        assert result.returncode != 0 and json.loads(result.stdout)['status'] == 'unsupported'
        path.write_bytes(b'<?php echo PHP_VERSION;')
        result = subprocess.run([str(ROOT / 'bin/php-semantics'), str(path)], capture_output=True, env=ENV, timeout=35, cwd=directory)
        negatives.append({'source': base64.b64encode(path.read_bytes()).decode(), 'command': result.args, 'exit_status': result.returncode, 'observation': json.loads(result.stdout)})
        assert result.returncode != 0 and json.loads(result.stdout)['status'] == 'unsupported'
        path.write_bytes(b'<?php echo "x";')
        result = subprocess.run([str(ROOT / 'bin/php-semantics'), str(path), '--steps', '0'], capture_output=True, env=ENV, timeout=35, cwd=directory)
        negatives.append({"source": base64.b64encode(path.read_bytes()).decode(), "command": result.args,
                          "exit_status": result.returncode, "observation": json.loads(result.stdout)})
        assert result.returncode != 0 and json.loads(result.stdout)['status'] == 'budget_exhausted'
        result = subprocess.run([str(ROOT / 'bin/php-semantics'), str(path), '--timeout', '0.000001'], capture_output=True, env=ENV, timeout=35, cwd=directory)
        negatives.append({"source": base64.b64encode(path.read_bytes()).decode(), "command": result.args,
                          "exit_status": result.returncode, "observation": json.loads(result.stdout)})
        assert result.returncode != 0 and json.loads(result.stdout)['status'] == 'timeout'
        result = subprocess.run([str(ROOT / 'bin/php-semantics'), str(path) + '.missing'], capture_output=True, env=ENV, timeout=35, cwd=directory)
        negatives.append({"source": base64.b64encode(path.read_bytes()).decode(), "command": result.args,
                          "exit_status": result.returncode, "observation": json.loads(result.stdout)})
        assert result.returncode != 0 and json.loads(result.stdout)['status'] == 'runner_failure'
        for source in [b'<?php f()[0]="X";', b'<?php echo $argc;', b'<?php $a=&$argc;',
                       b'<?php $n="argc"; $a=&$$n;', b'<?php unset($GLOBALS);',
                       b'<?php $n="GLOBALS"; unset($$n);', b'<?php echo $missing; ${NAN}=1;',
                       b'<?php echo $missing; ${INF-INF}=1;',
                       b'<?php echo MISSING; ${[]}=1;', b'<?php echo MISSING; ${[1]+[2]}=1;',
                       b'<?php $a="abc";unset($a[0][0]);',
                       b'<?php $a=[...[]];',
                       b'<?php echo $http_response_header;',
                       b'<?php $http_response_header=1;echo $http_response_header;']:
            path.write_bytes(source)
            result = subprocess.run([str(ROOT / 'bin/php-semantics'), str(path)], capture_output=True,
                                    env=ENV, timeout=35, cwd=directory)
            response = json.loads(result.stdout)
            assert result.returncode != 0 and response['status'] == 'unsupported', response
            negatives.append({'source': base64.b64encode(source).decode(), 'exit_status': result.returncode,
                              'observation': response})
        # Edited checked values cannot invent source positions for diagnostics.
        for line in (None, -1):
            meta = {} if line is None else {'startLine': {'int': str(line)}}
            expression = {'node': 'Expr_ConstFetch', 'fields': [
                {'node': 'Name', 'fields': [{'bytes': base64.b64encode(b'UNKNOWN_CONST').decode()}], 'meta': {}}], 'meta': meta}
            ast = {'version': 1, 'program': [{'node': 'Stmt_Expression', 'fields': [expression], 'meta': {}}]}
            payload = {'op': 'execute', 'ast': ast, 'steps': 100, 'filename': base64.b64encode(os.fsencode(path)).decode()}
            result = subprocess.run([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
                                    input=syntax_validation.wire.dumps(payload), text=True,
                                    capture_output=True, timeout=35, env=ENV, cwd=directory)
            response = syntax_validation.wire.loads(result.stdout)
            assert response.get('ok') and response['state']['COMPLETION']['tag'] == 'UNSUPPORTED', response
            negatives.append({'input': payload, 'exit_status': result.returncode, 'observation': response})
    # Warnings/errors also require source context on edited checked ASTs.
    for expression in [
        {'node': 'Expr_Array', 'fields': [[]], 'meta': {}},
        {'node': 'Scalar_Float', 'fields': [{'float': '7ff8000000000000'}], 'meta': {}},
        {'node': 'Expr_BinaryOp_Div', 'fields': [
            {'node': 'Scalar_Int', 'fields': [{'int': '1'}], 'meta': {}},
            {'node': 'Scalar_Int', 'fields': [{'int': '0'}], 'meta': {}}], 'meta': {}}]:
        payload = {'op': 'execute', 'steps': 100, 'filename': base64.b64encode(b'/edited.php').decode(), 'ast': {'version': 1, 'program': [
            {'node': 'Stmt_Echo', 'fields': [[expression]], 'meta': {}}]}}
        result = subprocess.run([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
                                input=syntax_validation.wire.dumps(payload), text=True,
                                capture_output=True, timeout=35, env=ENV)
        response = syntax_validation.wire.loads(result.stdout)
        assert response.get('ok') and response['state']['COMPLETION']['tag'] == 'UNSUPPORTED', response
        negatives.append({'input': payload, 'exit_status': result.returncode, 'observation': response})
    oracle_info = subprocess.run([str(PHP), '-n', *FLAGS, '-r',
        'echo json_encode(["version"=>PHP_VERSION,"sapi"=>PHP_SAPI,"int_size"=>PHP_INT_SIZE,"zts"=>PHP_ZTS,"extensions"=>get_loaded_extensions()]);'],
        capture_output=True, check=True, env=ENV, timeout=30)
    assert before == fingerprint(), 'implementation changed during run'
    oracle_identity = json.loads(oracle_info.stdout)
    assert (oracle_identity['version'], oracle_identity['sapi'], oracle_identity['int_size'], oracle_identity['zts']) == ('8.5.10', 'cli', 8, False)
    oracle_identity['binary_sha256'] = hashlib.sha256(PHP.read_bytes()).hexdigest()
    oracle_identity['source_commit'] = '34308a6666b2d489c509541ea9befea9e2b42348'
    report = {'selection_prefix': args.prefix, 'budgets': {'transitions': 100000, 'worker_seconds': 30, 'process_seconds': 35}, 'seeds': {'alias': 85010, 'scalar': 6614, 'array_keys': 7116}, 'scope': 'authored scalar, variable storage and array literal/read/write/unset plus variable and element reference-source checked execution fixtures', 'profile': PROFILE,
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'oracle': oracle_identity,
              'fingerprints': before, 'results': results, 'negative_checks': negatives}
    raw = ROOT / 'coverage' / ('results-semantic-source-selected.jsonl' if args.prefix else 'results-semantic-source.jsonl')
    raw.write_text(''.join(json.dumps(result) + '\n' for result in results))
    report['raw_results'] = {'path': str(raw.relative_to(ROOT)),
                             'sha256': hashlib.sha256(raw.read_bytes()).hexdigest(), 'records': len(results)}
    report['results'] = [{'id': result['id'], 'source_sha256': result['source_sha256'],
                          'semantic_status': result['semantic']['status'], 'comparison': result['comparison']}
                         for result in results]
    output = ROOT / 'coverage/semantics' / ('source-selected.json' if args.prefix else 'source.json') 
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(f'{len(results)} differential cases and {len(negatives)} outcome negatives passed')


if __name__ == '__main__':
    main()
