#!/usr/bin/env python3
"""Memoized coalescing assignment: source outcomes, ownership and resumption."""
from pathlib import Path
import base64,hashlib,json,re,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[2];D=ROOT;R=ROOT
sys.path.insert(0,str(R/'tests/semantics'));import static_types as t;import destructuring as d;import foreach as f

CASES = {'constant-variable-name-originals-empty-array/coalesce-write': b'<?php echo "A";${\n[]\n}??=7;e'
                                                                b'cho "B";',
 'constant-variable-name-originals-array/coalesce-write': b'<?php echo "A";${\n[1]\n}??=7;echo "B"'
                                                          b';',
 'constant-variable-name-originals-nan/coalesce-write': b'<?php echo "A";${\nNAN\n}??=7;echo "B";',
 'constant-variable-name-originals-infinity/coalesce-write': b'<?php echo "A";${\nINF\n}??=7;echo'
                                                             b' "B";',
 'constant-variable-name-originals-list-effect/coalesce-write': b'<?php echo "A";${\n(list($x)=[1])'
                                                                b'\n}??=7;echo "B";',
 'constant-variable-name-originals-list-nested-effect/coalesce-write': b'<?php echo "A";${\n(list('
                                                                       b'$x)=[[1]])\n}??=7;echo "B'
                                                                       b'";',
 'coalesce-assignment-lines-float-key-constant': b'<?php $a=[];\n$a[1.2+\n0] ??=\n7;',
 'coalesce-assignment-lines-float-key-temp': b'<?php $a=[];$k=1.2;\n$a[$k+\n0] ??=\n7;',
 'coalesce-assignment-lines-float-key-cv': b'<?php $a=[];$k=1.2;\n$a[\n$k] ??=\n7;',
 'coalesce-assignment-lines-float-key-nullbase': b'<?php $a=null;\n$a[1.2+\n0] ??=\n7;',
 'coalesce-assignment-lines-float-key-falsebase': b'<?php $a=false;\n$a[1.2+\n0] ??=\n7;',
 'coalesce-assignment-lines-float-key-truebase': b'<?php $a=true;\n$a[1.2+\n0] ??=\n7;',
 'coalesce-assignment-lines-float-key-selected': b'<?php $a=[1=>8];\n$a[1.2+\n0] ??=\n7;',
 'coalesce-assignment-lines-float-key-throwrhs': b'<?php $a=[];\n$a[1.2+\n0] ??=\n1/0;',
 'coalesce-assignment-lines-nested-falsebase': b'<?php $a=false;\n$a[1.2+\n0][2.3+\n0] ??=\n7;',
 'coalesce-assignment-lines-nested-truebase': b'<?php $a=true;\n$a[1.2+\n0][2.3+\n0] ??=\n7;',
 'coalesce-assignment-lines-nested-arraybase': b'<?php $a=[];\n$a[1.2+\n0][2.3+\n0] ??=\n7;',
 'coalesce-assignment-lines-key-array-early': b'<?php $a=[];\n$a[[]] ??=\n1/0;',
 'coalesce-assignment-lines-name-this-cv': b'<?php $n="this";\n${\n$n} ??=\n7;',
 'coalesce-assignment-lines-name-this-temp': b'<?php $n="this";\n${"".\n$n} ??=\n7;',
 'coalesce-assignment-lines-name-this-cast': b'<?php $n="this";\n${(string)\n$n} ??=\n7;',
 'coalesce-assignment-lines-key-undefined-cv': b'<?php $a=[];\n$a[\n$k] ??=\n7;',
 'coalesce-assignment-lines-key-undefined-temp': b'<?php $a=[];\n$a[$k+\n0] ??=\n7;',
 'coalesce-assignment-lines-name-undefined-cv': b'<?php ${\n$n} ??=\n7;',
 'coalesce-assignment-lines-name-undefined-temp': b'<?php ${"".\n$n} ??=\n7;',
 'review6-coalesce-reference-originals-key-reference-rhs-mutates': b'<?php $a=[];$j=1;$a[($k=&$j)'
                                                                   b']??=($j=2);echo $a[1]??"x","'
                                                                   b':",$a[2]??"x",":",$k;',
 'review6-coalesce-reference-originals-key-reference-rhs-rebinds': b'<?php $a=[];$j=1;$z=2;$a[($k'
                                                                   b'=&$j)]??=($j=&$z);echo $a[1]'
                                                                   b'??"x",":",$a[2]??"x",":",$k;',
 'review6-coalesce-reference-originals-key-reference-ternary-copy': b'<?php $a=[];$j=1;$a[(true?($'
                                                                    b'k=&$j):0)]??=($j=2);echo $a['
                                                                    b'1]??"x",":",$a[2]??"x",":",$'
                                                                    b'k;',
 'review6-coalesce-reference-originals-key-reference-dim-rhs-mutates': b'<?php $a=[];$j=[1];$a[($'
                                                                       b'k=&$j[0])]??=($j[0]=2);e'
                                                                       b'cho $a[1]??"x",":",$a[2]'
                                                                       b'??"x",":",$k;',
 'review6-coalesce-reference-originals-name-reference-rhs-mutates': b'<?php $j="a";${($k=&$j)}??=('
                                                                    b'$j="b");echo $a??"x",":",$b?'
                                                                    b'?"x",":",$k;',
 'review6-coalesce-reference-originals-name-reference-rhs-rebinds': b'<?php $j="a";$z="b";${($k=&$'
                                                                    b'j)}??=($j=&$z);echo $a??"x",'
                                                                    b'":",$b??"x",":",$k;',
 'review6-coalesce-reference-originals-name-reference-ternary-copy': b'<?php $j="a";${(true?($k=&$j'
                                                                     b'):0)}??=($j="b");echo $a??"x'
                                                                     b'",":",$b??"x",":",$k;',
 'review6-coalesce-reference-originals-key-reference-nonnull-cleanup': b'<?php $a=[1=>8];$j=1;ech'
                                                                       b'o $a[($k=&$j)]??=($j=2);'
                                                                       b'$k=3;echo ":",$j;',
 'review6-coalesce-reference-originals-key-reference-rhs-type-change': b'<?php $a=[];$j=1;$a[($k='
                                                                       b'&$j)]??=($j=[]);',
 'review6-coalesce-reference-originals-key-temp-rhs-type-change': b'<?php $a=[];$j=1;$a[$j+0]??='
                                                                  b'($j=[]);echo $a[1][0]??"x";',
 'review6-coalesce-reference-originals-nested-reference-key': b'<?php $a=[];$j=1;$n=3;$a[($k=&$j'
                                                              b')][$n]??=($j=$n=2);echo $a[1][3]'
                                                              b'??"x",":",$a[2][2]??"x";',
 'review6-coalesce-reference-originals-key-reference-rhs-throw': b'<?php $a=[];$j=1;$a[($k=&$j)]??='
                                                                 b'(1/0);',
 'assign-matrix--null': b'<?php $k=null;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix--0': b'<?php $k=0;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix--1.5': b'<?php $k=1.5;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix--"0x"': b'<?php $k="0x";$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix--[]': b'<?php $k=[];$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix--NAN': b'<?php $k=NAN;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=null;-null': b'<?php $a=null;$k=null;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=null;-0': b'<?php $a=null;$k=0;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=null;-1.5': b'<?php $a=null;$k=1.5;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=null;-"0x"': b'<?php $a=null;$k="0x";$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=null;-[]': b'<?php $a=null;$k=[];$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=null;-NAN': b'<?php $a=null;$k=NAN;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=false;-null': b'<?php $a=false;$k=null;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=false;-0': b'<?php $a=false;$k=0;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=false;-1.5': b'<?php $a=false;$k=1.5;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=false;-"0x"': b'<?php $a=false;$k="0x";$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=false;-[]': b'<?php $a=false;$k=[];$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=false;-NAN': b'<?php $a=false;$k=NAN;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=true;-null': b'<?php $a=true;$k=null;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=true;-0': b'<?php $a=true;$k=0;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=true;-1.5': b'<?php $a=true;$k=1.5;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=true;-"0x"': b'<?php $a=true;$k="0x";$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=true;-[]': b'<?php $a=true;$k=[];$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=true;-NAN': b'<?php $a=true;$k=NAN;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=7;-null': b'<?php $a=7;$k=null;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=7;-0': b'<?php $a=7;$k=0;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=7;-1.5': b'<?php $a=7;$k=1.5;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=7;-"0x"': b'<?php $a=7;$k="0x";$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=7;-[]': b'<?php $a=7;$k=[];$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=7;-NAN': b'<?php $a=7;$k=NAN;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a="";-null': b'<?php $a="";$k=null;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a="";-0': b'<?php $a="";$k=0;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a="";-1.5': b'<?php $a="";$k=1.5;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a="";-"0x"': b'<?php $a="";$k="0x";$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a="";-[]': b'<?php $a="";$k=[];$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a="";-NAN': b'<?php $a="";$k=NAN;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a="ab";-null': b'<?php $a="ab";$k=null;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a="ab";-0': b'<?php $a="ab";$k=0;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a="ab";-1.5': b'<?php $a="ab";$k=1.5;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a="ab";-"0x"': b'<?php $a="ab";$k="0x";$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a="ab";-[]': b'<?php $a="ab";$k=[];$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a="ab";-NAN': b'<?php $a="ab";$k=NAN;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=[];-null': b'<?php $a=[];$k=null;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=[];-0': b'<?php $a=[];$k=0;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=[];-1.5': b'<?php $a=[];$k=1.5;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=[];-"0x"': b'<?php $a=[];$k="0x";$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=[];-[]': b'<?php $a=[];$k=[];$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=[];-NAN': b'<?php $a=[];$k=NAN;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=[null,0];-null': b'<?php $a=[null,0];$k=null;$r=($a[$k]??=9);echo $r,":",$a[$k]'
                                    b'??"x";',
 'assign-matrix-$a=[null,0];-0': b'<?php $a=[null,0];$k=0;$r=($a[$k]??=9);echo $r,":",$a[$k]??"x";',
 'assign-matrix-$a=[null,0];-1.5': b'<?php $a=[null,0];$k=1.5;$r=($a[$k]??=9);echo $r,":",$a[$k]?'
                                   b'?"x";',
 'assign-matrix-$a=[null,0];-"0x"': b'<?php $a=[null,0];$k="0x";$r=($a[$k]??=9);echo $r,":",$a[$k]'
                                    b'??"x";',
 'assign-matrix-$a=[null,0];-[]': b'<?php $a=[null,0];$k=[];$r=($a[$k]??=9);echo $r,":",$a[$k]??'
                                  b'"x";',
 'assign-matrix-$a=[null,0];-NAN': b'<?php $a=[null,0];$k=NAN;$r=($a[$k]??=9);echo $r,":",$a[$k]?'
                                   b'?"x";',
 'assign-cv-absent': b'<?php echo $a??=7;echo $a;',
 'assign-cv-null': b'<?php $a=null;echo $a??=7;echo $a;',
 'assign-cv-reference': b'<?php $a=null;$b=&$a;echo $a??=7;echo $b;',
 'assign-cv-rebound-rhs': b'<?php $a=null;$b=8;echo $a??=($a=&$b);$a=7;echo $b;',
 'assign-rhs-short-circuit': b'<?php $a=0;$i=0;echo $a??=++$i;echo $i;',
 'assign-name-reread': b'<?php $n="a";echo $$n??=($n="b");echo $a??"x",$b??"x";',
 'assign-key-reread': b'<?php $a=[];$i=1;echo $a[$i]??=($i=2);echo $a[1]??"x",$a[2]??"x";',
 'assign-key-once': b'<?php $a=[];$i=1;echo $a[$i++]??=($i=4);echo $a[1]??"x",$a[4]??"x",$i;',
 'assign-array-rhs-cow': b'<?php $a=[];$b=[1];$c=($a[0]??=$b);$c[0]=7;echo $a[0][0],$b[0],$c[0];',
 'assign-array-self-rhs': b'<?php $a=[];$a[0]??=$a;echo $a[0]===[];',
 'assign-nested-key-effects': b'<?php $i=0;echo $a[$i++][$i++]??=($i=4);echo $a[0][1],$i;',
 'assign-nested-rhs-replacement': b'<?php $a=[[null]];echo $a[0][0]??=($a=[[7]]);echo $a[0][0][0'
                                  b'][0];',
 'assign-nonnull-key-temp': b'<?php $a=[7];$i=0;echo $a[$i++]??=($i=4);echo $i;',
 'assign-name-temp-array': b'<?php $n=[];echo $$n??=7;echo $$n;',
 'review6-coalesce-nested-originals-assign-present-result-cow': b'<?php $a=[1];$b=($a??=[2]);$b[0]'
                                                                b'=7;echo $a[0],$b[0];',
 'review6-coalesce-nested-originals-assign-present-result-reference': b'<?php $x=[1];$a=&$x;$b=('
                                                                      b'$a??=[2]);$b[0]=7;echo $'
                                                                      b'x[0],$b[0];',
 'review6-coalesce-nested-originals-assign-present-result-nested-reference': b'<?php $x=1;$a=[&$x];'
                                                                             b'$b=($a??=[2]);$b[0]='
                                                                             b'7;echo $x;',
 'review6-coalesce-nested-originals-assign-present-foreach-temporary': b'<?php $a=[1,2];foreach(('
                                                                       b'$a??=[]) as &$v){$v=7;}e'
                                                                       b'cho $a[0],$a[1],$v;',
 'review6-coalesce-nested-originals-assign-absent-foreach-temporary': b'<?php foreach(($a??=[1,2'
                                                                      b']) as &$v){$v=7;}echo $a'
                                                                      b'[0],$a[1],$v;',
 'review6-coalesce-nested-originals-assign-nested-key-reference': b'<?php $a=[];$b=[];$j=1;$a[($'
                                                                  b'k=&$j)]??=($b[$j]??=($j=2));'
                                                                  b'echo $a[2],$b[2],$k;',
 'review6-coalesce-nested-originals-assign-nested-name-reference': b'<?php $n="a";$m="b";${($x=&$'
                                                                   b'n)}??=(${($y=&$m)}??=($n=$m='
                                                                   b'"c"));echo $a??"x",$b??"x",$'
                                                                   b'c??"x",$x,$y;',
 'review6-coalesce-nested-originals-assign-nested-reference-rebind': b'<?php $a=[];$b=[];$j=1;$z=2;'
                                                                     b'$a[($k=&$j)]??=($b[($q=&$j)]'
                                                                     b'??=($j=&$z));echo $a[1],$b[1'
                                                                     b'],$k,$q,$j;',
 'review6-coalesce-nested-originals-assign-null-reference-target': b'<?php $x=null;$a=&$x;$b=($a?'
                                                                   b'?=[1]);$b[0]=7;echo $x[0],$b'
                                                                   b'[0];',
 'review6-coalesce-nested-originals-assign-self-reference-array': b'<?php $a=[];$r=&$a;$a[0]??=$'
                                                                  b'a;echo $a[0][0]??7,$r[0][0]?'
                                                                  b'?8;',
 'review6-coalesce-nested-originals-assign-list-key-effect': b'<?php $a=[];$r=($a[(list($k)=[1])[0]'
                                                             b']??=7);echo $k,$r,$a[1];',
 'review6-coalesce-nested-originals-assign-folded-name-effect': b'<?php ${(list($k)=[1])}??=7;echo'
                                                                b' $k,${[]};',
 'review6-coalesce-nested-originals-assign-nested-throw-cleanup': b'<?php $a=[];$b=[];$j=1;$a[($'
                                                                  b'k=&$j)]??=($b[($q=&$j)]??=(1'
                                                                  b'/0));',
 'review6-coalesce-nested-originals-assign-string-present-skip': b'<?php $a="abc";$j=1;echo $a[($k='
                                                                 b'&$j)]??=($j=2);echo $j,$k;',
 'review6-coalesce-nested-originals-assign-array-literal-multiple': b'<?php $a=[];$j=0;$b=[$a[$j++'
                                                                    b']??=1,$a[$j++]??=2];echo $b['
                                                                    b'0],$b[1],$j;',
 'review6-coalesce-nested-originals-assign-loop-origin': b'<?php $a=[];foreach([1,2] as &$v){echo $'
                                                         b'a[$v]??=$v;}echo $v;',
 'coalesce-assignment-guards-this': b'<?php $this ??= [,$x];',
 'coalesce-assignment-guards-this-concat': b'<?php ${"th"."is"} ??= [,$x];',
 'coalesce-assignment-guards-this-temp': b'<?php ${true?"this":"x"} ??= [,$x];',
 'coalesce-assignment-guards-globals': b'<?php $GLOBALS ??= [,$x];',
 'coalesce-assignment-guards-globals-temp': b'<?php ${true?"GLOBALS":"x"} ??= [,$x];',
 'coalesce-assignment-guards-function': b'<?php foo() ??= [,$x];',
 'coalesce-assignment-guards-method': b'<?php $x->foo() ??= [,$x];',
 'coalesce-assignment-guards-staticmethod': b'<?php C::foo() ??= [,$x];',
 'coalesce-assignment-guards-nullsafemethod': b'<?php $x?->foo() ??= [,$x];',
 'coalesce-assignment-guards-nullsafeprop': b'<?php $x?->p ??= [,$x];',
 'coalesce-assignment-guards-nullsafepropdim': b'<?php $x?->p[0] ??= [,$x];',
 'coalesce-assignment-guards-append': b'<?php $x[] ??= [,$x];',
 'coalesce-assignment-guards-temporary-dim': b'<?php [1][0] ??= 7;',
 'coalesce-assignment-guards-temporary-dim-hole-right': b'<?php [1][0] ??= [,$x];',
 'coalesce-assignment-guards-header-self': b'<?php $http_response_header ??= $http_response_heade'
                                           b'r;echo $http_response_header;',
 'coalesce-assignment-guards-header-dim-rhs': b'<?php $a[\n$k] ??=\n$http_response_header;echo $ht'
                                              b'tp_response_header;'}

PREFIX = f.PREFIX

def main():
    paths=json.loads((D/'spec/semantics/modules.json').read_text());out=Path(tempfile.mkdtemp(prefix='coalesce-assignment-state-',dir=ROOT/'.tools'))
    before=t.syntax_validation.implementation_fingerprint()
    manifest={p:hashlib.sha256((D/p).read_bytes()).hexdigest() for p in paths}
    selection=['review6-coalesce-reference-originals-key-reference-rhs-mutates', 'review6-coalesce-reference-originals-key-reference-rhs-rebinds', 'review6-coalesce-reference-originals-name-reference-rhs-rebinds', 'review6-coalesce-reference-originals-key-reference-rhs-type-change', 'review6-coalesce-reference-originals-key-reference-nonnull-cleanup', 'assign-array-rhs-cow', 'assign-nested-key-effects', 'review6-coalesce-reference-originals-key-reference-rhs-throw']
    rows=[{'id':name,'source_base64':base64.b64encode(CASES[name]).decode()} for name in selection]
    f=t.Worker([str(t.PHP),'-n',*t.FLAGS,'-d','extension='+str(R/'.tools/php-file.so'),str(D/'frontend/worker.php')]);a=t.Worker([str(R/'_build/default/adapter/main.exe'),str(D)])
    records=[]
    try:
     for i,row in enumerate(rows):
      source=base64.b64decode(row['source_base64']);p=out/f'case{i}.php';p.write_bytes(source);native=subprocess.run([str(t.PHP),'-n',*t.FLAGS,str(p)],capture_output=True,env=t.ENV,timeout=10)
      parsed=f.request({'op':'parse','source':row['source_base64']});checked=a.request({'op':'check','ast':parsed['ast'],'fixture':True})
      completion='NORMAL'
      if native.returncode==255:
       match=re.search(rb'Uncaught (Error|TypeError|DivisionByZeroError|ArithmeticError): (.*?) in '+re.escape(str(p).encode())+rb':(\d+)',native.stderr);assert match,native.stderr
       completion='THROWN '+json.dumps(match[1].decode())+' '+d.byte_sequence(match[2])+' '+match[3].decode()
      events=[]
      for severity,message,line in re.findall(rb'(Warning|Deprecated): (.*) in .* on line (\d+)',native.stderr):
       events.append('WARNING '+d.byte_sequence(message.removeprefix(b'Undefined variable $'))+' '+line.decode() if message.startswith(b'Undefined variable $') else 'DIAGNOSTIC "'+severity.decode()+'" '+d.byte_sequence(message)+' '+line.decode())
      checks=['S_initial = $php_run('+checked['fixture']+', 0, '+json.dumps(base64.b64encode(str(p).encode()).decode())+')','S_initial.COMPLETION = BUDGET','S = S_initial[.COMPLETION = NORMAL]','S_out = $drive(S, 10000)','$outputs(S_out.EVENTS) = '+d.byte_sequence(native.stdout),'$messages(S_out.EVENTS) = ['+', '.join(events)+']','S_out.COMPLETION = '+completion,'S_out.ORIGIN = eps','S_out.HELD = eps','S_out.ITERATORS = eps','S_out.TODO = eps','S_out.POOLS = S.POOLS','S_out.CODE = S.CODE','$heap_valid($heap_graph(S_out))','$foreach_valid(S_out)']
      for b in range(65):
       checks += [f'S_b{b} = $drive(S, {b})',f'$resume_foreach(S_b{b}, 10000) = S_out',f'S_b{b}.POOLS = S.POOLS',f'S_b{b}.CODE = S.CODE',f'S_b{b}.HELD = eps',f'$heap_valid($heap_graph(S_b{b}))',f'$foreach_valid(S_b{b})']
      q=out/f'case{i}.watsup';q.write_text(d.PREFIX+PREFIX+'dec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+x+'\n' for x in checks))
      records.append({'id':row['id'],'source_base64':row['source_base64'],'context':str(p),'oracle':{'stdout':base64.b64encode(native.stdout).decode(),'stderr':base64.b64encode(native.stderr).decode(),'exit_status':native.returncode},'assertions':len(checks),'fixture':str(q)})
     (out/'originals.json').write_text(json.dumps({'inputs':manifest,'records':records},indent=2)+'\n')
     for i,record in enumerate(records):
      run=subprocess.run([str(R/'tests/semantics/_build/default/numeric_runner.exe'),*[str(D/p) for p in paths],record['fixture']],capture_output=True,text=True,timeout=900)
      record['run']={'status':run.returncode,'stdout':run.stdout,'stderr':run.stderr};(out/f'result{i}.json').write_text(json.dumps(record,indent=2)+'\n');print(record['id'],run.returncode,run.stdout[:60],run.stderr[:200],flush=True)
    finally:f.close();a.close()
    assert manifest=={p:hashlib.sha256((D/p).read_bytes()).hexdigest() for p in paths}
    assert before==t.syntax_validation.implementation_fingerprint(),'coalescing assignment gate inputs changed'
    report={'fingerprint':before,'result':'pass' if all(x['run']['status']==0 and x['run']['stdout'].strip()=='true' for x in records) else 'fail','inputs':manifest,'records':records,'assertions':sum(x['assertions'] for x in records)};(out/'results.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'coverage/semantics/coalesce-assignment.json').write_text(json.dumps(report,indent=2)+'\n');assert report['result']=='pass',str(out);print(out,report['result'],report['assertions'])

if __name__=='__main__':main()
