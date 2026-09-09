#!/usr/bin/env python3
"""Destructuring: exact sources, effectful known results and resumption."""
import base64, json, re, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/semantics'))
import static_types as types

NORMAL_CASES = {
    'loop-author-effect-concat': b'<?php echo (list($a)=[1])."x";echo $a;',
    'loop-author-effect-array-key': b'<?php [(list($a)=[1])=>2];echo $a;',
    'loop-review-independent-list-effects-14': b'<?php $a=9;$b=8;echo ((list($a)=[]) ?? (list($b)=[2]))==[];echo $a,$b;',
    'loop-review-independent-list-effects-25': b'<?php $a=[];$i=0;for($j=0;$j<3;$j++){echo ((list($a[$i++])=[7])===[7]);}echo $i,$a[0],$a[1],$a[2];',
    'loop-review-independent-list-effects-26': b'<?php $a=[];$i=0;for($j=0;$j<3;$j++){echo (list($a[$i++])=[7])||(list($a[$i++])=[8]);}echo $i,$a[0],$a[1],$a[2];',
    'loop-review-independent-list-effects-27': b'<?php $a=[];$i=0;for($j=0;$j<3;$j++){echo (list($a[$i++])=[] )||(list($a[$i++])=[8]);}echo $i,$a[1],$a[3],$a[5];',
    'loop-coalesce-coalesce-list-loop': b'<?php $a=[];$i=0;while($i<3){(list($a[$i++])=[1])??[];}echo $i,$a[2];',
}

CASES = {
    'list-author-effect-and-empty': b'<?php $a=9;(list($a)=[]) && [,$x];echo $a;',
    'list-author-effect-or-nonempty': b'<?php $a=9;(list($a)=[1]) || [,$x];echo $a;',
    'list-author-effect-and-true': b'<?php (list($a)=[1]) && [,$x];',
    'list-author-effect-or-empty': b'<?php (list($a)=[]) || [,$x];',
    'list-author-effect-not': b'<?php $a=9;!(list($a)=[]) || [,$x];echo $a;',
    'list-author-effect-compare': b'<?php $a=9;((list($a)=[1])===[1]) || [,$x];echo $a;',
    'list-author-effect-cast': b'<?php $a=9;(bool)(list($a)=[1]) || [,$x];echo $a;',
    'list-author-effect-concat': b'<?php echo (list($a)=[1])."x";echo $a;',
    'list-author-effect-concat-variable': b'<?php $x="b";echo (list($a)=[1]).($x="z");echo $a;',
    'list-author-effect-array-key': b'<?php [(list($a)=[1])=>2];echo $a;',
    'list-author-effect-nested-list': b'<?php $a=9;$b=8;list($b)=(list($a)=[1]);echo $a,$b;',
    'list-author-effect-prepass': b'<?php $a=9;[(list($a)=[1]) || [,$x]];echo $a;',
    'list-review-independent-list-effects-0': b'<?php $a=9;$b=8;echo ((list($a)=[1])===(list($b)=[1]));echo $a,$b;',
    'list-review-independent-list-effects-1': b'<?php $a=9;$b=8;echo ((list($a)=[])===(list($b)=[]));echo $a,$b;',
    'list-review-independent-list-effects-2': b'<?php $a=9;$b=8;echo ((list($a)=[1])+(list($b)=[2]))[0];echo $a,$b;',
    'list-review-independent-list-effects-3': b'<?php $a=9;$b=8;echo ((list($a)=[])||(list($b)=[2]));echo $a,$b;',
    'list-review-independent-list-effects-4': b'<?php $a=9;$b=8;echo ((list($a)=[1])||(list($b)=[2]));echo $a,$b;',
    'list-review-independent-list-effects-5': b'<?php $a=9;$b=8;echo ((list($a)=[])&&(list($b)=[2]));echo $a,$b;',
    'list-review-independent-list-effects-6': b'<?php $a=9;$b=8;echo ((list($a)=[1])&&(list($b)=[2]));echo $a,$b;',
    'list-review-independent-list-effects-7': b'<?php $a=9;$b=8;echo !(list($a)=[]) && (list($b)=[2]);echo $a,$b;',
    'list-review-independent-list-effects-8': b'<?php $a=9;$b=8;echo ((list($a)=[1]) === [1]) || (list($b)=[2]);echo $a,$b;',
    'list-review-independent-list-effects-9': b'<?php $a=9;$b=8;echo ((list($a)=[1]) !== [1]) || (list($b)=[2]);echo $a,$b;',
    'list-review-independent-list-effects-10': b'<?php $a=9;$b=8;echo ((list($a)=[1]) <=> [1]) || (list($b)=[2]);echo $a,$b;',
    'list-review-independent-list-effects-11': b'<?php $a=9;$b=8;echo (bool)(list($a)=[1]) || (list($b)=[2]);echo $a,$b;',
    'list-review-independent-list-effects-12': b'<?php $a=9;$b=8;echo (list($a)=[1]) ? (list($b)=[2])[0] : (list($b)=[3])[0];echo $a,$b;',
    'list-review-independent-list-effects-13': b'<?php $a=9;$b=8;echo (list($a)=[]) ? (list($b)=[2])[0] : (list($b)=[3])[0];echo $a,$b;',
    'list-review-independent-list-effects-14': b'<?php $a=9;$b=8;echo ((list($a)=[]) ?? (list($b)=[2]))==[];echo $a,$b;',
    'list-review-independent-list-effects-15': b'<?php $a=9;$b=8;echo (list($a)=[1]).(list($b)=[2]);echo $a,$b;',
    'list-review-independent-list-effects-16': b'<?php $a=9;$b=8;echo (list($a)=[]).(list($b)=[]);echo $a,$b;',
    'list-review-independent-list-effects-17': b'<?php $a=9;$b=8;echo (list($a)=[1]).($a=2);echo $a,$b;',
    'list-review-independent-list-effects-18': b'<?php $a=9;$b=8;echo ($a=2).(list($a)=[1]);echo $a,$b;',
    'list-review-independent-list-effects-19': b'<?php $a=9;$b=8;echo (list($a,$b)=[1])."x";echo $a,$b;',
    'list-review-independent-list-effects-20': b'<?php $a=9;$b=8;list($b)=(list($a)=[1]);echo $a,$b;',
    'list-review-independent-list-effects-21': b'<?php $a=9;$b=8;list($b)=((list($a)=[1])+[2]);echo $a,$b;',
    'list-review-independent-list-effects-22': b'<?php $a=9;$b=8;$r=[(list($a)=[1]),(list($b)=[2])];echo $a,$b,$r[0][0],$r[1][0];',
    'list-review-independent-list-effects-23': b'<?php $a=9;$b=8;[(list($a)=[1])=>2];echo $a,$b;',
    'list-review-independent-list-effects-24': b'<?php $a=9;$b=8;echo (list($a)=[1]) / (list($b)=[2]);echo $a,$b;',
    'list-review-independent-list-effects-25': b'<?php $a=[];$i=0;for($j=0;$j<3;$j++){echo ((list($a[$i++])=[7])===[7]);}echo $i,$a[0],$a[1],$a[2];',
    'list-review-independent-list-effects-26': b'<?php $a=[];$i=0;for($j=0;$j<3;$j++){echo (list($a[$i++])=[7])||(list($a[$i++])=[8]);}echo $i,$a[0],$a[1],$a[2];',
    'list-review-independent-list-effects-27': b'<?php $a=[];$i=0;for($j=0;$j<3;$j++){echo (list($a[$i++])=[] )||(list($a[$i++])=[8]);}echo $i,$a[1],$a[3],$a[5];',
    'list-review-independent-list-effects-28': b'<?php $a=9;$b=8;echo ((list($a)=[])||true)||[,$x];echo $a,$b;',
    'list-review-independent-list-effects-29': b'<?php $a=9;$b=8;echo ((list($a)=[1])&&false)&&[,$x];echo $a,$b;',
    'list-review-independent-list-effects-30': b'<?php $a=9;$b=8;echo ((list($a)=[1])===[1])||[,$x];echo $a,$b;',
    'list-review-independent-list-effects-31': b'<?php $a=9;$b=8;echo (bool)(list($a)=[1])||[,$x];echo $a,$b;',
    'list-review-independent-list-effects-32': b'<?php $a=9;$b=8;echo [(list($a)=[1])||[,$x]];echo $a,$b;',
    'list-review-independent-list-effects-33': b'<?php $a=[];$i=0;echo ((list($a[$i++])=[1]) === (list($a[$i++])=[1]));echo $i,$a[0],$a[1];',
    'list-review-independent-list-effects-34': b'<?php $a=[];$i=0;list($a[$i++])=(list($a[$i++])=[1]);echo $i,$a[0],$a[1];',
    'list-review-independent-list-effects-35': b'<?php $a=[];$i=0;echo ((list($a[$i++])=[1])[0]) + ((list($a[$i++])=[2])[0]);echo $i,$a[0],$a[1];',
    'list-redirect-redirect-and': b'<?php $u=0;$a=9;(list($a)=[1])&&$u;echo $a;',
    'list-redirect-redirect-or': b'<?php $u=1;$a=9;(list($a)=[])||$u;echo $a;',
    'list-redirect-redirect-right-increment': b'<?php $u=1;echo (list($a)=[1])&&($u++);echo $a,$u;',
    'list-redirect-redirect-nested-right': b'<?php $u=0;$a=9;$b=8;(list($a)=[1])&&((list($b)=[2])&&$u);echo $a,$b;',
    'list-redirect-redirect-ordered-dim': b'<?php (list($a)=[1])&&(list($a[0])=[2]);',
    'list-redirect-redirect-right-effects': b'<?php $u=1;$i=0;$a=[];$b=[];(list($a[$i++])=[1])&&((list($b[$i++])=[2])&&$u);echo $i,$a[0],$b[1];',
    'list-redirect-redirect-short-skip': b'<?php $i=0;$a=[];$u=1;(list($a[$i++])=[])&&((list($a[$i++])=[2])&&$u);echo $i;',
    'list-redirect-redirect-or-right': b'<?php $i=0;$a=[];$u=1;(list($a[$i++])=[])||((list($a[$i++])=[2])&&$u);echo $i,$a[1];',
    'list-coalesce-coalesce-null': b'<?php echo null??"r";',
    'list-coalesce-coalesce-zero': b'<?php echo 0??"r";',
    'list-coalesce-coalesce-false': b'<?php echo false??"r";',
    'list-coalesce-coalesce-empty-string': b'<?php echo ""??"r";',
    'list-coalesce-coalesce-empty-array': b'<?php echo ([]??[1])===[];',
    'list-coalesce-coalesce-array': b'<?php echo ([1]??[])===[1];',
    'list-coalesce-coalesce-list-empty': b'<?php $a=9;$b=8;echo ((list($a)=[])??(list($b)=[2]))===[];echo $a,$b;',
    'list-coalesce-coalesce-list-value': b'<?php $a=9;$b=8;echo ((list($a)=[1])??(list($b)=[2]))===[1];echo $a,$b;',
    'list-coalesce-coalesce-rhs-copy': b'<?php $a=[1];$b=null??$a;$a[0]=2;echo $b[0];',
    'list-coalesce-coalesce-list-copy': b'<?php $a=[9];$b=(list($a[0])=[1])??[];$b[0]=2;echo $a[0],$b[0];',
    'list-coalesce-coalesce-both-compile': b'<?php echo 1??[,$x];',
    'list-coalesce-coalesce-prepass-skip': b'<?php echo [1??[,$x]][0];',
    'list-coalesce-coalesce-prepass-list': b'<?php [(list($a)=[1])??[,$x]];',
    'list-coalesce-coalesce-result-tmp': b'<?php (1??2)||[,$x];',
    'list-coalesce-coalesce-list-loop': b'<?php $a=[];$i=0;while($i<3){(list($a[$i++])=[1])??[];}echo $i,$a[2];',
    'list-coalesce-coalesce-nested': b'<?php echo null??(null??"r");',
    'list-coalesce-coalesce-left-error': b'<?php echo (1/0)??"r";',
    'list-coalesce-coalesce-right-error-skipped': b'<?php echo 1??(1/0);',
    'list-coalesce-coalesce-right-missing-line': b'<?php echo null??\n$missing;',
    'list-coalesce-coalesce-list-left-warning-line': b'<?php echo (list($a)=\n[])??\n"r";',
    'list-list-destructure-0': b'<?php $a=[1,2];[$a,$b]=$a;echo $a,$b;',
    'list-list-destructure-1': b'<?php $a=[1,2];[$a[0],$b]=$a;echo $a[0],$a[1],$b;',
    'list-list-destructure-2': b'<?php $a=[1,2];[&$a,&$b]=$a;echo $a,$b;$a=3;echo $b;',
    'list-list-destructure-3': b'<?php $a=[1,2];[$a[0],&$b]=$a;$b=3;echo $a[0],$a[1];',
    'list-list-destructure-4': b'<?php $a=[1,2];[$a[0],$b]=($r=&$a);echo $a[0],$b;',
    'list-list-destructure-5': b'<?php $a=[1,2];[($a[0]=1)=>$b,1=>$c]=$a;echo $b,$c,$a[0];',
    'list-list-destructure-6': b'<?php $a=[1,2];[$a[0]=>$a[1]]=$a;echo $a[0],$a[1];',
    'list-list-destructure-7': b'<?php $a=[1,2];[$missing=>$b]=$a;echo $b;',
    'list-list-destructure-8': b'<?php $a=[1,2];[[]=>$b]=$a;echo $b;',
    'list-list-destructure-9': b'<?php $a=[[1,2],3];[[$a,$b],$c]=$a;echo $a,$b,$c;',
    'list-list-destructure-10': b'<?php $a=[[1,2],3];[[&$a,&$b],$c]=$a;echo $a,$b,$c;',
    'list-list-destructure-11': b'<?php $x=1;$a=[&$x,2];unset($x);[$b,$c]=$a;$b=3;echo $a[0],$b,$c;',
    'list-list-destructure-12': b'<?php $x=1;$a=[&$x,2];[$b,$c]=$a;$b=3;echo $x,$a[0],$b,$c;',
    'list-list-destructure-13': b'<?php $a=[];[$x,$y]=$a;echo $x===null,$y===null;',
    'list-list-destructure-14': b'<?php $a=[];[&$x,&$y]=$a;$x=1;$y=2;echo $a[0],$a[1];',
    'list-list-destructure-15': b'<?php $a=[1,2];[$x,,$y]=$a;echo $x,$y;',
    'list-list-destructure-16': b'<?php $a=[1,2];$r=([$x,$y]=$a);echo $r===$a;',
    'list-list-destructure-17': b'<?php $a=[1,2];$r=([&$x,&$y]=$a);$x=3;echo $r[0],$a[0];',
    'list-list-destructure-18': b'<?php [$missing=>$a]=null;echo $a===null;',
    'list-list-destructure-19': b'<?php [$missing=>$a]="abc";echo $a===null;',
    'list-list-destructure-scalar-null-': b'<?php $a=null;[$x,$y]=$a;echo $x===null,$y===null;',
    'list-list-destructure-scalar-null-&': b'<?php $a=null;[&$x,&$y]=$a;echo $x===null,$y===null;',
    'list-list-destructure-scalar-false-': b'<?php $a=false;[$x,$y]=$a;echo $x===null,$y===null;',
    'list-list-destructure-scalar-false-&': b'<?php $a=false;[&$x,&$y]=$a;echo $x===null,$y===null;',
    'list-list-destructure-scalar-true-': b'<?php $a=true;[$x,$y]=$a;echo $x===null,$y===null;',
    'list-list-destructure-scalar-true-&': b'<?php $a=true;[&$x,&$y]=$a;echo $x===null,$y===null;',
    'list-list-destructure-scalar-1-': b'<?php $a=1;[$x,$y]=$a;echo $x===null,$y===null;',
    'list-list-destructure-scalar-1-&': b'<?php $a=1;[&$x,&$y]=$a;echo $x===null,$y===null;',
    'list-list-destructure-scalar-1.5-': b'<?php $a=1.5;[$x,$y]=$a;echo $x===null,$y===null;',
    'list-list-destructure-scalar-1.5-&': b'<?php $a=1.5;[&$x,&$y]=$a;echo $x===null,$y===null;',
    'list-list-destructure-scalar-"abc"-': b'<?php $a="abc";[$x,$y]=$a;echo $x===null,$y===null;',
    'list-list-destructure-scalar-"abc"-&': b'<?php $a="abc";[&$x,&$y]=$a;echo $x===null,$y===null;',
    'list-list-more-key-value-0-0': b'<?php $k=null;$a=[0=>1,1=>2,"1x"=>3];[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-0-0': b'<?php $k=null;$a=[0=>1,1=>2,"1x"=>3];[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-0-1': b'<?php $k=null;$a=null;[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-0-1': b'<?php $k=null;$a=null;[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-0-2': b'<?php $k=null;$a=false;[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-0-2': b'<?php $k=null;$a=false;[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-0-3': b'<?php $k=null;$a="abc";[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-0-3': b'<?php $k=null;$a="abc";[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-1-0': b'<?php $k=false;$a=[0=>1,1=>2,"1x"=>3];[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-1-0': b'<?php $k=false;$a=[0=>1,1=>2,"1x"=>3];[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-1-1': b'<?php $k=false;$a=null;[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-1-1': b'<?php $k=false;$a=null;[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-1-2': b'<?php $k=false;$a=false;[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-1-2': b'<?php $k=false;$a=false;[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-1-3': b'<?php $k=false;$a="abc";[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-1-3': b'<?php $k=false;$a="abc";[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-2-0': b'<?php $k=true;$a=[0=>1,1=>2,"1x"=>3];[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-2-0': b'<?php $k=true;$a=[0=>1,1=>2,"1x"=>3];[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-2-1': b'<?php $k=true;$a=null;[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-2-1': b'<?php $k=true;$a=null;[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-2-2': b'<?php $k=true;$a=false;[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-2-2': b'<?php $k=true;$a=false;[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-2-3': b'<?php $k=true;$a="abc";[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-2-3': b'<?php $k=true;$a="abc";[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-3-0': b'<?php $k=1.5;$a=[0=>1,1=>2,"1x"=>3];[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-3-0': b'<?php $k=1.5;$a=[0=>1,1=>2,"1x"=>3];[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-3-1': b'<?php $k=1.5;$a=null;[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-3-1': b'<?php $k=1.5;$a=null;[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-3-2': b'<?php $k=1.5;$a=false;[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-3-2': b'<?php $k=1.5;$a=false;[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-3-3': b'<?php $k=1.5;$a="abc";[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-3-3': b'<?php $k=1.5;$a="abc";[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-4-0': b'<?php $k=NAN;$a=[0=>1,1=>2,"1x"=>3];[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-4-0': b'<?php $k=NAN;$a=[0=>1,1=>2,"1x"=>3];[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-4-1': b'<?php $k=NAN;$a=null;[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-4-1': b'<?php $k=NAN;$a=null;[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-4-2': b'<?php $k=NAN;$a=false;[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-4-2': b'<?php $k=NAN;$a=false;[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-4-3': b'<?php $k=NAN;$a="abc";[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-4-3': b'<?php $k=NAN;$a="abc";[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-5-0': b'<?php $k=[];$a=[0=>1,1=>2,"1x"=>3];[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-5-0': b'<?php $k=[];$a=[0=>1,1=>2,"1x"=>3];[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-5-1': b'<?php $k=[];$a=null;[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-5-1': b'<?php $k=[];$a=null;[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-5-2': b'<?php $k=[];$a=false;[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-5-2': b'<?php $k=[];$a=false;[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-5-3': b'<?php $k=[];$a="abc";[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-5-3': b'<?php $k=[];$a="abc";[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-6-0': b'<?php $k="1";$a=[0=>1,1=>2,"1x"=>3];[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-6-0': b'<?php $k="1";$a=[0=>1,1=>2,"1x"=>3];[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-6-1': b'<?php $k="1";$a=null;[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-6-1': b'<?php $k="1";$a=null;[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-6-2': b'<?php $k="1";$a=false;[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-6-2': b'<?php $k="1";$a=false;[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-6-3': b'<?php $k="1";$a="abc";[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-6-3': b'<?php $k="1";$a="abc";[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-7-0': b'<?php $k="1x";$a=[0=>1,1=>2,"1x"=>3];[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-7-0': b'<?php $k="1x";$a=[0=>1,1=>2,"1x"=>3];[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-7-1': b'<?php $k="1x";$a=null;[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-7-1': b'<?php $k="1x";$a=null;[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-7-2': b'<?php $k="1x";$a=false;[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-7-2': b'<?php $k="1x";$a=false;[$k=>&$x]=$a;echo $x;',
    'list-list-more-key-value-7-3': b'<?php $k="1x";$a="abc";[$k=>$x]=$a;echo $x;',
    'list-list-more-key-reference-7-3': b'<?php $k="1x";$a="abc";[$k=>&$x]=$a;echo $x;',
    'list-list-more-interference-0': b'<?php $a=[1,2];[$a[],$a[]]=$a;echo $a[0],$a[1],$a[2],$a[3];',
    'list-list-more-interference-1': b'<?php $a=[1,2];[&$a[],&$a[]]=$a;$a[2]=3;echo $a[0],$a[1],$a[2],$a[3];',
    'list-list-more-interference-2': b'<?php $a=[1,2];[$a[($a=[9])[0]-9],$b]=$a;echo $a[0],$b;',
    'list-list-more-interference-3': b'<?php $a=[1,2];[&$a[($a=[9])[0]-9],&$b]=$a;echo $a[0],$b;',
    'list-list-more-interference-4': b'<?php $a=[1,2];$b=[3,4];[$a[($a=&$b)[0]-3],$x]=$a;echo $a[0],$b[0],$x;',
    'list-list-more-interference-5': b'<?php $a=[1,2];$b=[3,4];[&$a[($a=&$b)[0]-3],&$x]=$a;echo $a[0],$b[0],$x;',
    'list-list-more-interference-6': b'<?php $a=[1,2];$n="x";[${($n="y")},$$n]=$a;echo $y;',
    'list-list-more-interference-7': b'<?php $a=[1,2];$n="x";[&${($n="y")},&$$n]=$a;$y=3;echo $a[0],$a[1];',
    'list-list-more-interference-8': b'<?php $a=[1,2];[0=>$a[1],1=>$x]=$a;echo $a[0],$a[1],$x;',
    'list-list-more-interference-9': b'<?php $a=[1,2];[0=>$a[1],1=>&$x]=$a;echo $a[0],$a[1],$x;',
    'list-list-more-interference-10': b'<?php $a=[1,2];[0=>&$a[1],1=>$x]=$a;echo $a[0],$a[1],$x;',
    'list-list-more-interference-11': b'<?php $a=[[1,2],[3,4]];[[&$x,$y],[$z,&$w]]=$a;$x=5;$w=6;echo $a[0][0],$a[1][1],$y,$z;',
    'list-list-more-interference-12': b'<?php $a=[[1,2],[3,4]];[[$a,$b],[$c,$d]]=$a;echo $a,$b,$c,$d;',
    'list-list-more-interference-13': b'<?php $a=[[1,2],[3,4]];[[&$a,&$b],[&$c,&$d]]=$a;echo $a,$b,$c,$d;',
    'list-list-more-interference-14': b'<?php $a=[];$a[0]=&$a;[$b]=$a;echo $a===$b;',
    'list-list-more-interference-15': b'<?php $a=[];$a[0]=&$a;[&$b]=$a;echo $a===$b;',
    'list-list-more-interference-16': b'<?php $a=[];$a[0]=&$a;[[&$b]]=$a;echo $a===$b;',
    'list-list-more-interference-17': b'<?php $a=[1,2];$b=$a;[&$x,&$y]=$a;$x=3;echo $a[0],$b[0],$y;',
    'list-list-more-interference-18': b'<?php $x=1;$a=[&$x];unset($x);$b=$a;[$y]=$a;$y=2;echo $a[0],$b[0],$y;',
    'list-list-more-interference-19': b'<?php $a=[1,2];$x="abc";[$y,$x[0]]=$a;echo $y,$x;',
    'list-list-more-interference-20': b'<?php $a=[1,2];$x="abc";[$y,&$x[0]]=$a;echo $y;',
    'list-list-more-interference-21': b'<?php $a=[1,2];$x=true;[$y,$x[0]]=$a;echo $y;',
    'list-list-more-interference-22': b'<?php $a=[1,2];$x=false;[$y,$x[0]]=$a;echo $y,$x[0];',
    'list-list-more-interference-23': b'<?php $a=[1,2];$x=false;[$y,&$x[0]]=$a;echo $y,$x[0];',
    'list-list-more-interference-24': b'<?php $a=[1,2];$x=1;$r=&$x;$a[1]=&$r;[$y,&$r]=$a;echo $y,$r;',
    'list-list-more-interference-25': b'<?php $a=[1,2];[$a,[$b,$c]]=$a;echo $a,$b,$c;',
    'list-list-more-interference-26': b'<?php $a=[1,2];[&$a,[&$b,&$c]]=$a;echo $a,$b,$c;',
    'list-list-cv-list-cv-0': b'<?php [$a]=$this;echo $a;',
    'list-list-cv-list-cv-1': b'<?php [$a]=${"th"."is"};echo $a;',
    'list-list-cv-list-cv-2': b'<?php [$a]=${true?"this":"other"};echo $a;',
    'list-list-cv-list-cv-3': b'<?php [&$a]=$this;',
    'list-list-cv-list-cv-4': b'<?php [$a]=$missing;echo $a;',
    'list-list-line-value-vars': b'<?php [\n$a,\n$b\n]=\n[];',
    'list-list-line-value-dim': b'<?php [\n$a[\n"k"\n],\n$b\n]=\n[];',
    'list-list-line-value-append': b'<?php [\n$a[],\n$b\n]=\n[];',
    'list-list-line-value-computed': b'<?php $n="x";[\n${$n\n. "y"},\n$b\n]=\n[];',
    'list-list-line-ref-vars': b'<?php $rhs=[];[\n&$a,\n$b\n]=\n$rhs;',
    'list-list-line-ref-dim': b'<?php $rhs=[];[\n&$a[\n"k"\n],\n$b\n]=\n$rhs;',
    'list-list-line-ref-computed': b'<?php $rhs=[];$n="x";[\n&${$n\n. "y"},\n$b\n]=\n$rhs;',
    'list-list-line-keyed-vars': b'<?php [\n"a"\n=>\n$x,\n"b"=>\n$y\n]=\n[];',
    'list-list-line-keyed-dim': b'<?php [\n"a"\n=>\n$x[\n"t"\n],\n"b"=>\n$y\n]=\n[];',
    'list-list-line-nested': b'<?php [\n[\n$a,\n$b\n],\n$c\n]=\n[];',
    'list-list-line-nested-ref': b'<?php $rhs=[];[\n[\n&$a,\n$b\n],\n$c\n]=\n$rhs;',
    'list-list-line-holes': b'<?php [\n$a[\n"t"\n],\n,\n$b\n]=\n[];',
    'list-list-line-dim-error': b'<?php $a=1;[\n$a[\n"k"\n],\n$b\n]=\n[2];',
    'list-list-line-computed-warning': b'<?php [\n${$n\n. "y"},\n$b\n]=\n[];',
    'list-list-line-style-after-rhs': b'<?php [list($x)] = [[]=>1];',
    'list-list-line-ref-before-rhs': b'<?php [&$x] = [[]=>1];',
    'list-list-line-key-before-style': b'<?php [[[]=>1]=>list($x)] = [];',
    'list-list-line-key-before-target': b'<?php [[[]=>1]=>foo()] = [];',
    'list-list-line-empty-after-rhs': b'<?php [] = [[]=>1];',
    'list-list-line-keyed-hole-after-rhs': b'<?php [,"x"=>$a] = [[]=>1];',
    'list-list-rhs-line-cv-known': b'<?php $rhs=[];[\n$a,\n$b\n]=\n$rhs;',
    'list-list-rhs-line-cv-missing': b'<?php [\n$a,\n$b\n]=\n$rhs;',
    'list-list-rhs-line-cv-firsthole': b'<?php $rhs=[];[\n,\n$a\n]=\n$rhs;',
    'list-list-rhs-line-cv-empty': b'<?php $rhs=[];[\n]=\n$rhs;',
    'list-list-rhs-line-cv-keyed': b'<?php $rhs=[];[\n"k"\n=>$a\n]=\n$rhs;',
    'list-list-rhs-line-computed-known': b'<?php $rhs=[];$n="rhs";[\n$a,\n$b\n]=\n${$n};',
    'list-list-rhs-line-computed-missing': b'<?php [\n$a,\n$b\n]=\n${$n};',
    'list-list-rhs-line-computed-folded': b'<?php $rhs=[];[\n$a,\n$b\n]=\n${"r"\n."hs"};',
    'list-list-rhs-line-computed-ternary': b'<?php $rhs=[];[\n$a,\n$b\n]=\n${true\n?"rhs":"no"};',
    'list-list-rhs-line-cv-reference': b'<?php $rhs=[];[\n&$a,\n$b\n]=\n$rhs;',
    'list-list-rhs-line-cv-this': b'<?php [\n$a,\n$b\n]=\n$this;',
    'list-list-spread-spread-value': b'<?php [...$x]=[];',
    'list-list-spread-spread-ref-operand': b'<?php [...[&$x]]=[];',
    'list-list-spread-spread-nested-ref': b'<?php [...[[&$x]]]=[];',
    'list-list-spread-spread-no-ref-array': b'<?php [...[$x]]=[];',
    'list-list-spread-spread-nested-spread': b'<?php [...[...$x]]=[];',
    'list-list-spread-spread-early-rhs': b'<?php [...$x]=[[]=>1];',
    'list-list-spread-spread-ref-early-rhs': b'<?php [...[&$x]]=[[]=>1];',
    'list-list-spread-spread-ref-variable': b'<?php $r=[];[...[&$x]]=$r;',
    'list-list-spread-spread-ref-nullsafe': b'<?php [...[&$x]]=$r?->p;',
    'list-list-spread-spread-after-ref': b'<?php [&$x,...$y]=[];',
    'list-list-spread-spread-keyed-first': b'<?php ["k"=>$x,...$y]=[];',
    'list-list-spread-spread-unkeyed-first': b'<?php [...$x,"k"=>$y]=[];',
    'list-coalesce-phase-coalesce-list-visits-hole': b'<?php (list($a)=[1])??[,$x];',
    'list-coalesce-phase-coalesce-list-tmp-visits-hole': b'<?php ((list($a)=[1])??[2])||[,$x];',
    'list-coalesce-phase-coalesce-literal-array-visits-hole': b'<?php [1]??[,$x];',
    'list-coalesce-phase-coalesce-prepass-array-skip': b'<?php [[1]??[,$x]];',
    'list-dim-0-true': b'<?php $src=[1,2];$x=true;\n[\n$x[\n0\n],\n$y\n]=\n$src;echo $x[0],$y;',
    'list-dim-0-false': b'<?php $src=[1,2];$x=false;\n[\n$x[\n0\n],\n$y\n]=\n$src;echo $x[0],$y;',
    'list-dim-0-"abc"': b'<?php $src=[1,2];$x="abc";\n[\n$x[\n0\n],\n$y\n]=\n$src;echo $x[0],$y;',
    'list-dim-1-true': b'<?php $src=[1,2];$x=true;\n[\n&$x[\n0\n],\n$y\n]=\n$src;echo $x[0],$y;',
    'list-dim-1-false': b'<?php $src=[1,2];$x=false;\n[\n&$x[\n0\n],\n$y\n]=\n$src;echo $x[0],$y;',
    'list-dim-1-"abc"': b'<?php $src=[1,2];$x="abc";\n[\n&$x[\n0\n],\n$y\n]=\n$src;echo $x[0],$y;',
    'list-name-0': b'<?php $src=[1,2];$name=[];\n[\n${\n$name\n},\n$y\n]=\n$src;echo $Array,$y;',
    'list-key-0': b'<?php $src=[1,2];$x=[];$key=[];\n[\n$x[\n$key\n],\n$y\n]=\n$src;',
    'list-nested-0': b'<?php $src=[1,2];$x=false;\n[\n$x[\n0\n][\n0\n],\n$y\n]=\n$src;echo $x[0][0],$y;',
    'list-name-1': b'<?php $src=[1,2];$name=[];\n[\n&${\n$name\n},\n$y\n]=\n$src;echo $Array,$y;',
    'list-key-1': b'<?php $src=[1,2];$x=[];$key=[];\n[\n&$x[\n$key\n],\n$y\n]=\n$src;',
    'list-nested-1': b'<?php $src=[1,2];$x=false;\n[\n&$x[\n0\n][\n0\n],\n$y\n]=\n$src;echo $x[0][0],$y;',
}

PREFIX = '''
dec $resume_destructuring(pstate, nat) : pstate
def $resume_destructuring(S, n) = $drive(S[.COMPLETION = NORMAL], n) -- if S.COMPLETION = BUDGET
def $resume_destructuring(S, n) = S -- if S.COMPLETION =/= BUDGET

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
                source_path=Path(tmp)/f'destructuring-{len(records):03}.php'
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
                                   f'$resume_destructuring(S_budget{budget}, 10000) = S_out',
                                   f'S_budget{budget}.POOLS = S.POOLS',
                                   f'S_budget{budget}.CODE = S.CODE',
                                   f'$heap_valid($heap_graph(S_budget{budget}))']
                assertions.append(checks)
                records.append({'id':name,'source_base64':base64.b64encode(source).decode(),'ast':checked['ast'],
                                'oracle_exit_status':native.returncode,'oracle_stdout':base64.b64encode(native.stdout).decode(),
                                'oracle_stderr':base64.b64encode(native.stderr).decode()})
            for index,checks in enumerate(assertions):
                fixture=Path(tmp)/'destructuring.watsup'
                fixture.write_text(PREFIX+'dec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+check+'\n' for check in checks))
                run=subprocess.run([str(runner),*map(str,specs),str(fixture)],capture_output=True,text=True,cwd=ROOT,timeout=120)
                if run.returncode or run.stdout.strip()!='true':
                    (ROOT/'.tools/destructuring-source-failure.watsup').write_text(fixture.read_text())
                    raise AssertionError((index,run.stdout,run.stderr))
    finally:
        frontend.close();adapter.close()
    assert before==types.syntax_validation.implementation_fingerprint(),'inputs changed during destructuring gate'
    report={'result':'pass','classification':'checked-source destructuring, effectful known results and nonvariable coalesce; ownership and budget resumption',
            'source_cases':len(records),'state_cases':len(assertions),'assertions':sum(map(len,assertions)),
            'records':records,'fingerprint':before}
    (ROOT/'coverage/semantics/destructuring.json').write_text(json.dumps(report,indent=2)+'\n')
    print({key:report[key] for key in ('result','source_cases','state_cases','assertions')})

if __name__=='__main__':
    main()
