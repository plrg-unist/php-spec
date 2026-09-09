#!/usr/bin/env python3
"""Array foreach: exact checked sources, cursor ownership and budget resumption."""
from pathlib import Path
import base64,hashlib,json,re,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[2];D=ROOT;R=ROOT
sys.path.insert(0,str(ROOT/'tests/semantics'));import static_types as t;import destructuring as d

CASES = {
    'ref-expression-direct': b'<?php $b=[1,2];foreach(($a=&$b) as &$v){echo $v;if($v==1){$b[]=3;}}echo $a[2];',
    'ref-expression-rebind': b'<?php $b=[1,2];foreach(($a=&$b) as &$v){echo $v;if($v==1){$b=[7,8];}}echo $a[0];',
    'ref-expression-dim': b'<?php $b=[[1,2]];foreach(($a=&$b[0]) as &$v){echo $v;if($v==1){$b[0][]=3;}}echo $a[2];',
    'ref-expression-ternary': b'<?php $b=[1,2];foreach((true?($a=&$b):[]) as &$v){echo $v;if($v==1){$b[]=3;}}echo $a[2];',
    'ref-expression-assignment': b'<?php $b=[1,2];foreach(($a=$b) as &$v){echo $v;if($v==1){$b[]=3;}}echo $b[2];',
    'copy-unwind-union-right': b'<?php $a=[1,2,3];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if(++$i===2)$a=$a+[9=>8];if($i>6)break;}echo "end";',
    'copy-unwind-union-left': b'<?php $a=[1,2,3];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if(++$i===2)$a=[9=>8]+$a;if($i>6)break;}echo "end";',
    'copy-unwind-spread': b'<?php $a=[1,2,3];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if(++$i===2)$a=[...$a,8];if($i>6)break;}echo "end";',
    'copy-unwind-identity-union': b'<?php $a=[1,2,3];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if(++$i===2)$a=$a+[];if($i>6)break;}echo "end";',
    'copy-unwind-empty-left-union': b'<?php $a=[1,2,3];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if(++$i===2)$a=[]+$a;if($i>6)break;}echo "end";',
    'copy-unwind-nested-continue-outer': b'<?php $a=[1,2];$b=[3,4];foreach($a as &$v){foreach($b as &$w){echo $v,$w;continue 2;}}$v=8;$w=9;echo ":",$a[0],$a[1],$b[0],$b[1];',
    'copy-unwind-nested-break-outer': b'<?php $a=[1,2];$b=[3,4];foreach($a as &$v){foreach($b as &$w){echo $v,$w;break 2;}}$v=8;$w=9;echo ":",$a[0],$a[1],$b[0],$b[1];',
    'copy-unwind-nested-throw': b'<?php $a=[1,2];$b=[3,4];foreach($a as &$v){foreach($b as &$w){echo $v,$w;$z=1/0;}}echo "bad";',
    'copy-unwind-reference-target-is-source': b'<?php $a=[[1,2],[3,4]];$i=0;foreach($a as &$a){echo $a[0],$a[1];if(++$i>4)break;}echo ":",$i;',
    'copy-unwind-value-key-target-is-source': b'<?php $a=[1,2];foreach($a as $a=>$v){echo $a,$v;}echo ":",$a;',
    'copy-unwind-reference-key-target-is-source': b'<?php $a=[1,2];foreach($a as $a=>&$v){echo $a,$v;}echo ":",$a,$v;',
    'initial-foreach-value-0': b'<?php $a=[1];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if($i++==0){unset($a[$k]);$a[$k]=2;}if($i>4)break;}',
    'initial-foreach-reference-0': b'<?php $a=[1];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if($i++==0){unset($a[$k]);$a[$k]=2;}if($i>4)break;}',
    'initial-foreach-value-1': b'<?php $a=["k"=>1];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if($i++==0){unset($a[$k]);$a[$k]=2;}if($i>4)break;}',
    'initial-foreach-reference-1': b'<?php $a=["k"=>1];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if($i++==0){unset($a[$k]);$a[$k]=2;}if($i>4)break;}',
    'initial-foreach-value-2': b'<?php $a=[1,2,3];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if($i++==0){unset($a[1]);$a[1]=4;}if($i>4)break;}',
    'initial-foreach-reference-2': b'<?php $a=[1,2,3];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if($i++==0){unset($a[1]);$a[1]=4;}if($i>4)break;}',
    'initial-foreach-value-3': b'<?php $a=["a"=>1,"b"=>2,"c"=>3];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if($i++==0){unset($a["b"]);$a["b"]=4;}if($i>4)break;}',
    'initial-foreach-reference-3': b'<?php $a=["a"=>1,"b"=>2,"c"=>3];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if($i++==0){unset($a["b"]);$a["b"]=4;}if($i>4)break;}',
    'initial-foreach-value-4': b'<?php $a=[1,2,3];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if($i++==0){unset($a[2]);$a[2]=4;}if($i>4)break;}',
    'initial-foreach-reference-4': b'<?php $a=[1,2,3];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if($i++==0){unset($a[2]);$a[2]=4;}if($i>4)break;}',
    'initial-foreach-value-5': b'<?php $a=["a"=>1,"b"=>2,"c"=>3];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if($i++==0){unset($a["c"]);$a["c"]=4;}if($i>4)break;}',
    'initial-foreach-reference-5': b'<?php $a=["a"=>1,"b"=>2,"c"=>3];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if($i++==0){unset($a["c"]);$a["c"]=4;}if($i>4)break;}',
    'initial-foreach-value-6': b'<?php $a=[1,2];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if($i++==0){$a[]=3;}if($i>4)break;}',
    'initial-foreach-reference-6': b'<?php $a=[1,2];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if($i++==0){$a[]=3;}if($i>4)break;}',
    'initial-foreach-value-7': b'<?php $a=[1,2];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if($i++==0){$a=[3,4];}if($i>4)break;}',
    'initial-foreach-reference-7': b'<?php $a=[1,2];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if($i++==0){$a=[3,4];}if($i>4)break;}',
    'initial-foreach-value-8': b'<?php $a=[1,2];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if($i++==0){$b=$a;$a[1]=3;}if($i>4)break;}',
    'initial-foreach-reference-8': b'<?php $a=[1,2];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if($i++==0){$b=$a;$a[1]=3;}if($i>4)break;}',
    'initial-foreach-value-9': b'<?php $a=[1,2];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if($i++==0){$b=[3,4];$a=&$b;}if($i>4)break;}',
    'initial-foreach-reference-9': b'<?php $a=[1,2];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if($i++==0){$b=[3,4];$a=&$b;}if($i>4)break;}',
    'initial-foreach-value-10': b'<?php $a=[1,2];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if($i++==0){unset($a);$a=[3,4];}if($i>4)break;}',
    'initial-foreach-reference-10': b'<?php $a=[1,2];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if($i++==0){unset($a);$a=[3,4];}if($i>4)break;}',
    'initial-foreach-value-11': b'<?php $a=[2=>1,4=>2];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if($i++==0){unset($a[4]);$a[3]=3;$a[4]=4;}if($i>4)break;}',
    'initial-foreach-reference-11': b'<?php $a=[2=>1,4=>2];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if($i++==0){unset($a[4]);$a[3]=3;$a[4]=4;}if($i>4)break;}',
    'initial-foreach-value-12': b'<?php $a=[1,2];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if($i++==0){$a["z"]=3;unset($a[1]);$a[1]=4;}if($i>4)break;}',
    'initial-foreach-reference-12': b'<?php $a=[1,2];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if($i++==0){$a["z"]=3;unset($a[1]);$a[1]=4;}if($i>4)break;}',
    'initial-foreach-value-13': b'<?php $a=["z"=>0,0=>1,1=>2];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if($i++==0){unset($a["z"]);unset($a[1]);$a[1]=4;}if($i>4)break;}',
    'initial-foreach-reference-13': b'<?php $a=["z"=>0,0=>1,1=>2];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if($i++==0){unset($a["z"]);unset($a[1]);$a[1]=4;}if($i>4)break;}',
    'history-foreach-copy-history-0-0': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;$b[2]=8;}if($i===2)$a=$b;}echo "end";',
    'history-foreach-copy-history-0-1': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;$a[2]=8;}if($i===2)$a=$b;}echo "end";',
    'history-foreach-copy-history-0-2': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;$b[2]=8;}if($i===2){$a=$b;$a[3]=9;}}echo "end";',
    'history-foreach-copy-history-0-3': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;$b[2]=8;$c=$b;$c[2]=9;}if($i===2)$a=$c;}echo "end";',
    'history-foreach-copy-history-0-4': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;$b[2]=8;$c=$b;$c[2]=9;}if($i===2)$a=$b;if($i===3)$a=$c;}echo "end";',
    'history-foreach-copy-history-0-5': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;$b[2]=8;}if($i===2){unset($b[1]);$a=$b;}}echo "end";',
    'history-foreach-copy-history-0-6': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;$b[2]=8;}if($i===2){unset($b[1]);$b[1]=7;$a=$b;}}echo "end";',
    'history-foreach-copy-history-0-7': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){unset($a[1]);$b=$a;$b[2]=8;}if($i===2)$a=$b;}echo "end";',
    'history-foreach-copy-history-0-8': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){unset($a[1],$a[2]);$b=$a;$b[3]=8;}if($i===2)$a=$b;}echo "end";',
    'history-foreach-copy-history-0-9': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){unset($a[0],$a[1],$a[2]);$b=$a;$b[3]=8;$a=$b;}}echo "end";',
    'history-foreach-copy-history-0-10': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;unset($b[0],$b[1],$b[2]);$b[3]=8;$a=$b;}}echo "end";',
    'history-foreach-copy-history-0-11': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;$b[2]=8;}if($i===2){$a=[];$a[3]=9;}}echo "end";',
    'history-foreach-copy-history-0-12': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;$b[2]=8;}if($i===2){$a=&$b;$a[3]=9;}}echo "end";',
    'history-foreach-copy-history-0-13': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;$b[2]=8;}if($i===2){unset($a);$a=$b;}}echo "end";',
    'history-foreach-copy-history-0-14': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){unset($a[1]);$a[1]=8;}if($i===2){unset($a[2]);$a[2]=9;}}echo "end";',
    'history-foreach-copy-history-1-0': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;$b[2]=8;}if($i===2)$a=$b;}echo "end";',
    'history-foreach-copy-history-1-1': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;$a[2]=8;}if($i===2)$a=$b;}echo "end";',
    'history-foreach-copy-history-1-2': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;$b[2]=8;}if($i===2){$a=$b;$a[3]=9;}}echo "end";',
    'history-foreach-copy-history-1-3': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;$b[2]=8;$c=$b;$c[2]=9;}if($i===2)$a=$c;}echo "end";',
    'history-foreach-copy-history-1-4': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;$b[2]=8;$c=$b;$c[2]=9;}if($i===2)$a=$b;if($i===3)$a=$c;}echo "end";',
    'history-foreach-copy-history-1-5': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;$b[2]=8;}if($i===2){unset($b[1]);$a=$b;}}echo "end";',
    'history-foreach-copy-history-1-6': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;$b[2]=8;}if($i===2){unset($b[1]);$b[1]=7;$a=$b;}}echo "end";',
    'history-foreach-copy-history-1-7': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){unset($a[1]);$b=$a;$b[2]=8;}if($i===2)$a=$b;}echo "end";',
    'history-foreach-copy-history-1-8': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){unset($a[1],$a[2]);$b=$a;$b[3]=8;}if($i===2)$a=$b;}echo "end";',
    'history-foreach-copy-history-1-9': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){unset($a[0],$a[1],$a[2]);$b=$a;$b[3]=8;$a=$b;}}echo "end";',
    'history-foreach-copy-history-1-10': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;unset($b[0],$b[1],$b[2]);$b[3]=8;$a=$b;}}echo "end";',
    'history-foreach-copy-history-1-11': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;$b[2]=8;}if($i===2){$a=[];$a[3]=9;}}echo "end";',
    'history-foreach-copy-history-1-12': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;$b[2]=8;}if($i===2){$a=&$b;$a[3]=9;}}echo "end";',
    'history-foreach-copy-history-1-13': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;$b[2]=8;}if($i===2){unset($a);$a=$b;}}echo "end";',
    'history-foreach-copy-history-1-14': b'<?php $a=[0,1,2];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){unset($a[1]);$a[1]=8;}if($i===2){unset($a[2]);$a[2]=9;}}echo "end";',
    'setup-absent-cv-value': b'<?php\n\nforeach(\n$a\nas $v){echo "body";}\necho $a;',
    'setup-absent-cv-ref': b'<?php\n\nforeach(\n$a\nas &$v){echo "body";}\necho $a;',
    'setup-null-cv-value': b'<?php\n$a=null;\nforeach(\n$a\nas $v){echo "body";}\necho $a;',
    'setup-null-cv-ref': b'<?php\n$a=null;\nforeach(\n$a\nas &$v){echo "body";}\necho $a;',
    'setup-false-cv-value': b'<?php\n$a=false;\nforeach(\n$a\nas $v){echo "body";}\n$a[0][0]=1;',
    'setup-false-cv-ref': b'<?php\n$a=false;\nforeach(\n$a\nas &$v){echo "body";}\n$a[0][0]=1;',
    'setup-false-ref-cv-value': b'<?php\n$a=false;$r=&$a;\nforeach(\n$a\nas $v){echo "body";}\n$a[0][0]=1;',
    'setup-false-ref-cv-ref': b'<?php\n$a=false;$r=&$a;\nforeach(\n$a\nas &$v){echo "body";}\n$a[0][0]=1;',
    'setup-int-cv-value': b'<?php\n$a=7;\nforeach(\n$a\nas $v){echo "body";}\necho $a;',
    'setup-int-cv-ref': b'<?php\n$a=7;\nforeach(\n$a\nas &$v){echo "body";}\necho $a;',
    'setup-string-cv-value': b'<?php\n$a="a";\nforeach(\n$a\nas $v){echo "body";}\necho $a;',
    'setup-string-cv-ref': b'<?php\n$a="a";\nforeach(\n$a\nas &$v){echo "body";}\necho $a;',
    'setup-absent-dim-value': b'<?php\n$a=[];\nforeach(\n$a[0]\nas $v){echo "body";}\necho $a[0];',
    'setup-absent-dim-ref': b'<?php\n$a=[];\nforeach(\n$a[0]\nas &$v){echo "body";}\necho $a[0];',
    'setup-false-dim-value': b'<?php\n$a=[false];\nforeach(\n$a[0]\nas $v){echo "body";}\n$a[0][0][0]=1;',
    'setup-false-dim-ref': b'<?php\n$a=[false];\nforeach(\n$a[0]\nas &$v){echo "body";}\n$a[0][0][0]=1;',
    'setup-false-ref-dim-value': b'<?php\n$x=false;$a=[&$x];\nforeach(\n$a[0]\nas $v){echo "body";}\n$a[0][0][0]=1;',
    'setup-false-ref-dim-ref': b'<?php\n$x=false;$a=[&$x];\nforeach(\n$a[0]\nas &$v){echo "body";}\n$a[0][0][0]=1;',
    'setup-false-computed-value': b'<?php\n$a=false;$n="a";\nforeach(\n$$n\nas $v){echo "body";}\n$a[0][0]=1;',
    'setup-false-computed-ref': b'<?php\n$a=false;$n="a";\nforeach(\n$$n\nas &$v){echo "body";}\n$a[0][0]=1;',
    'setup-absent-computed-value': b'<?php\n$n="a";\nforeach(\n$$n\nas $v){echo "body";}\necho $a;',
    'setup-absent-computed-ref': b'<?php\n$n="a";\nforeach(\n$$n\nas &$v){echo "body";}\necho $a;',
    'setup-absent-deep-value': b'<?php\n$a=[];\nforeach(\n$a[0][1]\nas $v){echo "body";}\necho $a[0][1];',
    'setup-absent-deep-ref': b'<?php\n$a=[];\nforeach(\n$a[0][1]\nas &$v){echo "body";}\necho $a[0][1];',
    'setup-temporary-value-false': b'<?php foreach(false as $v){echo $v;} echo "end";',
    'setup-temporary-value-null': b'<?php foreach(null as $v){echo $v;} echo "end";',
    'setup-temporary-value-7': b'<?php foreach(7 as $v){echo $v;} echo "end";',
    'setup-temporary-value-"s"': b'<?php foreach("s" as $v){echo $v;} echo "end";',
    'setup-temporary-value-[]': b'<?php foreach([] as $v){echo $v;} echo "end";',
    'setup-temporary-value-[1,2]': b'<?php foreach([1,2] as $v){echo $v;} echo "end";',
    'setup-temporary-ref-false': b'<?php foreach(false as &$v){echo $v;} echo "end";',
    'setup-temporary-ref-null': b'<?php foreach(null as &$v){echo $v;} echo "end";',
    'setup-temporary-ref-7': b'<?php foreach(7 as &$v){echo $v;} echo "end";',
    'setup-temporary-ref-"s"': b'<?php foreach("s" as &$v){echo $v;} echo "end";',
    'setup-temporary-ref-[]': b'<?php foreach([] as &$v){echo $v;} echo "end";',
    'setup-temporary-ref-[1,2]': b'<?php foreach([1,2] as &$v){echo $v;} echo "end";',
    'offset-foreach-offset-0': b'<?php $a="abc";foreach($a[0] as &$v){}',
    'offset-foreach-offset-1': b'<?php $a="abc";foreach($a[] as &$v){}',
    'offset-foreach-offset-2': b'<?php $a="abc";foreach($a[0][0] as &$v){}',
    'offset-foreach-offset-3': b'<?php foreach(($a=[1,2]) as &$v){echo $v;}echo $a[1];',
    'independent-alias-tail-byvalue': b'<?php $a=["x"=>1,"y"=>2,"z"=>3];foreach($a as &$v){}foreach($a as $k=>$v){echo $k,$v;}echo ":",$a["x"],$a["y"],$a["z"];',
    'independent-holder-replaced': b'<?php $h=[[1,2,3]];$i=0;foreach($h[0] as &$v){echo $v;if(++$i===1)$h=[[7,8]];}echo ":",$h[0][0];$v=9;echo $h[0][1];',
    'independent-holder-element-rebound': b'<?php $h=[[1,2,3]];$b=[7,8];$i=0;foreach($h[0] as &$v){echo $v;if(++$i===1)$h[0]=&$b;}echo ":",$b[0],$b[1];',
    'independent-holder-element-unset': b'<?php $h=[[1,2,3]];$i=0;foreach($h[0] as &$v){echo $v;if(++$i===1){unset($h[0]);$h[0]=[7,8];}}echo ":",$h[0][0],$h[0][1];',
    'independent-temporary-tail': b'<?php foreach([[1],[2]] as &$v){echo $v[0];}$v[0]=7;echo $v[0];',
    'independent-nested-shared-cursors': b'<?php $a=[1,2,3];$i=0;foreach($a as $k=>&$v){echo "o",$k,$v;if(++$i>3)break;$j=0;foreach($a as $q=>&$w){echo "i",$q,$w;if(++$j===1){$a[2]+=1;break;}}}echo ":",$a[2];',
    'independent-nested-copy-selected': b'<?php $a=[1,2,3];$i=0;foreach($a as $k=>&$v){echo "o",$k,$v;if(++$i>5)break;if($i===1){$b=$a;$b[2]=8;foreach($b as $q=>&$w){echo "i",$q,$w;if($q===1){$a=$b;break;}}}}echo ":",$a[2];',
    'independent-break-alias-tail': b'<?php $a=[1,2];foreach($a as &$v){break;}$v=8;echo $a[0],$a[1];unset($v);$b=$a;$b[0]=9;echo $a[0],$b[0];',
    'independent-replace-with-scalar': b'<?php $a=[1,2];foreach($a as &$v){echo $v;$a=3;}echo ":",$a,$v;',
    'independent-list-reference-tail': b'<?php $a=[[1,2],[3,4]];foreach($a as [$x,&$y]){echo $x,$y;}$y=8;echo ":",$a[0][1],$a[1][1];',
    'independent-value-descendant-choice': b'<?php $a=[1,2,3];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;$b[2]=8;$c=$a;$c[2]=9;}if($i===2)$a=$b;if($i===3)$a=$c;}echo "end";',
    'independent-value-named-source-rebind': b'<?php $a=[1,2,3];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=[7,8];$a=&$b;}$v+=1;}echo "end";',
    'independent-value-saved-copy-delete-reinsert': b'<?php $a=[1,2,3];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;$b[2]=8;}if($i===2){unset($b[1]);$b[1]=9;$a=$b;}}echo "end";',
    'independent-value-empty-copy-refill': b'<?php $a=[1,2,3];$i=0;foreach($a as $k=>$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){unset($a[0],$a[1],$a[2]);$b=$a;$b[4]=9;$a=$b;}}echo "end";',
    'independent-reference-descendant-choice': b'<?php $a=[1,2,3];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;$b[2]=8;$c=$a;$c[2]=9;}if($i===2)$a=$b;if($i===3)$a=$c;}echo "end";',
    'independent-reference-named-source-rebind': b'<?php $a=[1,2,3];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=[7,8];$a=&$b;}$v+=1;}echo "end";',
    'independent-reference-saved-copy-delete-reinsert': b'<?php $a=[1,2,3];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){$b=$a;$b[2]=8;}if($i===2){unset($b[1]);$b[1]=9;$a=$b;}}echo "end";',
    'independent-reference-empty-copy-refill': b'<?php $a=[1,2,3];$i=0;foreach($a as $k=>&$v){echo $k,":",$v,";";if(++$i>6)break;if($i===1){unset($a[0],$a[1],$a[2]);$b=$a;$b[4]=9;$a=$b;}}echo "end";',
    'multiline-0': b'<?php $x=false;\nforeach(\n[[1,2]]\nas\n$x[\n0\n]\n){echo $missing;}',
    'multiline-1': b'<?php $x=true;\nforeach(\n[[1,2]]\nas\n$x[\n0\n]\n){echo $missing;}',
    'multiline-2': b'<?php $n=[];\nforeach(\n[[1,2]]\nas\n${\n$n\n}\n){echo $missing;}',
    'multiline-3': b'<?php $x=false;\nforeach(\n[[1,2]]\nas\n[$x[\n0\n],\n$y]\n){echo $missing;}',
    'multiline-4': b'<?php $x=false;\nforeach(\n[[1,2]]\nas\n&$x[\n0\n]\n){echo $missing;}',
    'multiline-5': b'<?php $x=true;\nforeach(\n[[1,2]]\nas\n&$x[\n0\n]\n){echo $missing;}',
    'multiline-6': b'<?php $n=[];\nforeach(\n[[1,2]]\nas\n&${\n$n\n}\n){echo $missing;}',
    'multiline-scalar-cv': b'<?php $a=false;\nforeach(\n$a\nas\n&$v\n){}',
    'multiline-scalar-expression': b'<?php foreach(\n(1\n+2)\nas\n&$v\n){}',
    'multiline-key-error': b'<?php $k=true;\nforeach(\n[1]\nas\n$k[\n0\n]\n=>\n$v\n){}echo $v;',
    'multiline-value-then-key': b'<?php $k=false;$v=false;\nforeach(\n[1]\nas\n$k[\n0\n]\n=>\n$v[\n1\n]\n){}',
    'prerequisite-value-ref': b'<?php foreach([] as &$v){}',
    'prerequisite-value-ref-dim': b'<?php foreach([] as &$v[0]){}',
    'prerequisite-value-list-ref': b'<?php foreach([] as [&$v]){}',
    'prerequisite-value-nested-ref': b'<?php foreach([] as [[&$v]]){}',
    'prerequisite-value-list-hole': b'<?php foreach([] as [,$v,]){}',
    'prerequisite-value-genuine-hole': b'<?php foreach([] as list(,$v,)){}',
    'prerequisite-value-list-unpack': b'<?php foreach([] as [...$v]){}',
    'prerequisite-value-nested-unpack-ref': b'<?php foreach([] as [...[&$v]]){}',
    'prerequisite-value-long-nested': b'<?php foreach([] as [array($v)]){}',
    'prerequisite-value-mixed': b'<?php foreach([] as [list($v)]){}',
    'prerequisite-key-call': b'<?php foreach([] as foo()=>$v){}',
    'prerequisite-key-nullsafe': b'<?php foreach([] as $k?->p=>$v){}',
}

PREFIX = 'dec $resume_foreach(pstate, nat) : pstate\ndef $resume_foreach(S, n) = $drive(S[.COMPLETION = NORMAL], n) -- if S.COMPLETION = BUDGET\ndef $resume_foreach(S, n) = S -- if S.COMPLETION =/= BUDGET\n\ndec $cursor_valid(pstate, pcursor*) : bool\ndef $cursor_valid(S, eps) = true\ndef $cursor_valid(S, (CURSOR n_table n_position) :: pcursor*) = ($heap_member(HARRAY n_table, S.ALLOCATIONS) /\\ $(n_table < |S.ARRAYS|) /\\ $(n_position <= S.ARRAYS[n_table].SERIAL) /\\ $cursor_position(pcursor*, n_table) = eps /\\ $cursor_valid(S, pcursor*))\n\ndec $foreach_task_ids(ptask) : nat*\ndef $foreach_task_ids(AT porigin ptask) = $foreach_task_ids(ptask)\ndef $foreach_task_ids(FOREACH_NEXT n pnode statement porigin? z) = [n]\ndef $foreach_task_ids(ptask) = eps -- otherwise\ndec $foreach_tasks_ids(ptask*) : nat*\ndef $foreach_tasks_ids(eps) = eps\ndef $foreach_tasks_ids(ptask :: ptask_tail*) = $foreach_task_ids(ptask) ++ $foreach_tasks_ids(ptask_tail*)\ndec $foreach_ids(piterator*) : nat*\ndef $foreach_ids(eps) = eps\ndef $foreach_ids((ITERATOR n n_array b pcursor*) :: piterator*) = n :: $foreach_ids(piterator*)\ndec $foreach_id_count(nat*, nat) : nat\ndef $foreach_id_count(eps, n) = 0\ndef $foreach_id_count(n :: n_tail*, n) = $(1 + $foreach_id_count(n_tail*, n))\ndef $foreach_id_count(n_other :: n_tail*, n) = $foreach_id_count(n_tail*, n) -- if n_other =/= n\n\ndec $foreach_registry_valid(pstate, piterator*) : bool\ndef $foreach_registry_valid(S, eps) = true\ndef $foreach_registry_valid(S, (ITERATOR n n_array b pcursor*) :: piterator*) = ($(n < S.NEXTITER) /\\ $foreach_id_count($foreach_tasks_ids(S.TODO), n) = 1 /\\ $iterator_lookup(piterator*, n) = eps /\\ $cursor_valid(S, pcursor*) /\\ ($heap_member(HARRAY n_array, S.ALLOCATIONS) = ($cursor_position(pcursor*, n_array) =/= eps)) /\\ $foreach_registry_valid(S, piterator*))\n\ndec $foreach_origin_valid(pstate, porigin?) : bool\ndef $foreach_origin_valid(S, eps) = true\ndef $foreach_origin_valid(S, (porigin)) = ($origin_node(S.SOURCES, porigin) =/= eps)\ndec $foreach_task_valid(pstate, ptask) : bool\ndef $foreach_task_valid(S, AT porigin ptask) = ($origin_accepts(S.SOURCES, porigin, ptask) /\\ $foreach_task_valid(S, ptask))\ndef $foreach_task_valid(S, FOREACH_NEXT n pnode statement (porigin) z) = ($origin_node(S.SOURCES, porigin) = (statement) /\\ $heap_member(pnode, S.ALLOCATIONS))\ndef $foreach_task_valid(S, ORIGIN_RETURN porigin?) = $foreach_origin_valid(S, porigin?)\ndef $foreach_task_valid(S, ptask) = true -- otherwise\ndec $foreach_tasks_valid(pstate, ptask*) : bool\ndef $foreach_tasks_valid(S, eps) = true\ndef $foreach_tasks_valid(S, ptask :: ptask_tail*) = ($foreach_task_valid(S, ptask) /\\ $foreach_tasks_valid(S, ptask_tail*))\n\ndec $foreach_positions_valid(pentry*, pposition*, nat, nat) : bool\ndef $foreach_positions_valid(eps, eps, n_min, n_serial) = true\ndef $foreach_positions_valid((ENTRY pkey pitem) :: pentry*, (POSITION pkey n) :: pposition*, n_min, n_serial) = ($(n >= n_min) /\\ $(n < n_serial) /\\ $position_lookup(pposition*, pkey) = eps /\\ $foreach_positions_valid(pentry*, pposition*, $(n + 1), n_serial))\ndef $foreach_positions_valid(pentry*, pposition*, n_min, n_serial) = false -- otherwise\ndec $foreach_arrays_valid(parray*) : bool\ndef $foreach_arrays_valid(eps) = true\ndef $foreach_arrays_valid(parray :: parray_tail*) = ($foreach_positions_valid(parray.ITEMS, parray.POSITIONS, 0, parray.SERIAL) /\\ $foreach_arrays_valid(parray_tail*))\ndec $foreach_valid(pstate) : bool\ndef $foreach_valid(S) = ($foreach_registry_valid(S, S.ITERATORS) /\\ |$foreach_tasks_ids(S.TODO)| = |S.ITERATORS| /\\ $foreach_arrays_valid(S.ARRAYS) /\\ $foreach_origin_valid(S, S.ORIGIN) /\\ $foreach_tasks_valid(S, S.TODO))\n'

def main():
    paths=json.loads((D/'spec/semantics/modules.json').read_text());out=Path(tempfile.mkdtemp(prefix='foreach-state-',dir=ROOT/'.tools'))
    before=t.syntax_validation.implementation_fingerprint()
    manifest={p:hashlib.sha256((D/p).read_bytes()).hexdigest() for p in paths}
    selection=['independent-holder-element-rebound','setup-absent-dim-ref','ref-expression-rebind','ref-expression-direct','independent-nested-copy-selected','independent-reference-descendant-choice','copy-unwind-nested-continue-outer','copy-unwind-nested-break-outer','copy-unwind-nested-throw']
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
      for b in range(101):
       checks += [f'S_b{b} = $drive(S, {b})',f'$resume_foreach(S_b{b}, 10000) = S_out',f'S_b{b}.POOLS = S.POOLS',f'S_b{b}.CODE = S.CODE',f'S_b{b}.HELD = eps',f'$heap_valid($heap_graph(S_b{b}))',f'$foreach_valid(S_b{b})']
      q=out/f'case{i}.watsup';q.write_text(d.PREFIX+PREFIX+'dec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+x+'\n' for x in checks))
      records.append({'id':row['id'],'source_base64':row['source_base64'],'context':str(p),'oracle':{'stdout':base64.b64encode(native.stdout).decode(),'stderr':base64.b64encode(native.stderr).decode(),'exit_status':native.returncode},'assertions':len(checks),'fixture':str(q)})
     (out/'originals.json').write_text(json.dumps({'inputs':manifest,'records':records},indent=2)+'\n')
     for i,record in enumerate(records):
      run=subprocess.run([str(R/'tests/semantics/_build/default/numeric_runner.exe'),*[str(D/p) for p in paths],record['fixture']],capture_output=True,text=True,timeout=900)
      record['run']={'status':run.returncode,'stdout':run.stdout,'stderr':run.stderr};(out/f'result{i}.json').write_text(json.dumps(record,indent=2)+'\n');print(record['id'],run.returncode,run.stdout[:60],run.stderr[:200],flush=True)
    finally:f.close();a.close()
    assert manifest=={p:hashlib.sha256((D/p).read_bytes()).hexdigest() for p in paths}
    assert before==t.syntax_validation.implementation_fingerprint(),'foreach gate inputs changed'
    report={'fingerprint':before,'result':'pass' if all(x['run']['status']==0 and x['run']['stdout'].strip()=='true' for x in records) else 'fail','inputs':manifest,'records':records,'assertions':sum(x['assertions'] for x in records)};(out/'results.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'coverage/semantics/foreach.json').write_text(json.dumps(report,indent=2)+'\n');assert report['result']=='pass',str(out);print(out,report['result'],report['assertions'])

if __name__=='__main__':main()
