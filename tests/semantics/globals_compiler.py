#!/usr/bin/env python3
"""GLOBALS key-name conversion, compiler CV order and preserved operand facts."""
import base64,hashlib,json,subprocess,tempfile
from pathlib import Path
import source_compiler as compiler
from source_compiler import types,context
ROOT=Path(__file__).resolve().parents[2]
REPORT=ROOT/'coverage/semantics/globals-compiler.json'
PREFIX=compiler.PREFIX

SOURCES = [('key/empty-array/read', b'<?php echo "A";echo $GLOBALS[\n[]\n];echo "B";'),
 ('key/empty-array/write', b'<?php echo "A";$GLOBALS[\n[]\n]=7;echo "B";'),
 ('key/empty-array/unset', b'<?php echo "A";unset($GLOBALS[\n[]\n]);echo "B";'),
 ('key/empty-array/quiet', b'<?php echo "A";echo $GLOBALS[\n[]\n]??7;echo "B";'),
 ('key/empty-array/coalesce-write', b'<?php echo "A";$GLOBALS[\n[]\n]??=7;echo "B";'),
 ('key/empty-array/reference', b'<?php echo "A";$r=&$GLOBALS[\n[]\n];echo "B";'),
 ('key/array/read', b'<?php echo "A";echo $GLOBALS[\n[1]\n];echo "B";'),
 ('key/array/write', b'<?php echo "A";$GLOBALS[\n[1]\n]=7;echo "B";'),
 ('key/array/unset', b'<?php echo "A";unset($GLOBALS[\n[1]\n]);echo "B";'),
 ('key/array/quiet', b'<?php echo "A";echo $GLOBALS[\n[1]\n]??7;echo "B";'),
 ('key/array/coalesce-write', b'<?php echo "A";$GLOBALS[\n[1]\n]??=7;echo "B";'),
 ('key/array/reference', b'<?php echo "A";$r=&$GLOBALS[\n[1]\n];echo "B";'),
 ('key/nan/read', b'<?php echo "A";echo $GLOBALS[\nNAN\n];echo "B";'),
 ('key/nan/write', b'<?php echo "A";$GLOBALS[\nNAN\n]=7;echo "B";'),
 ('key/nan/unset', b'<?php echo "A";unset($GLOBALS[\nNAN\n]);echo "B";'),
 ('key/nan/quiet', b'<?php echo "A";echo $GLOBALS[\nNAN\n]??7;echo "B";'),
 ('key/nan/coalesce-write', b'<?php echo "A";$GLOBALS[\nNAN\n]??=7;echo "B";'),
 ('key/nan/reference', b'<?php echo "A";$r=&$GLOBALS[\nNAN\n];echo "B";'),
 ('key/infinity/read', b'<?php echo "A";echo $GLOBALS[\nINF\n];echo "B";'),
 ('key/infinity/write', b'<?php echo "A";$GLOBALS[\nINF\n]=7;echo "B";'),
 ('key/infinity/unset', b'<?php echo "A";unset($GLOBALS[\nINF\n]);echo "B";'),
 ('key/infinity/quiet', b'<?php echo "A";echo $GLOBALS[\nINF\n]??7;echo "B";'),
 ('key/infinity/coalesce-write', b'<?php echo "A";$GLOBALS[\nINF\n]??=7;echo "B";'),
 ('key/infinity/reference', b'<?php echo "A";$r=&$GLOBALS[\nINF\n];echo "B";'),
 ('key/list-effect/read', b'<?php echo "A";echo $GLOBALS[\n(list($x)=[1])\n];echo "B";'),
 ('key/list-effect/write', b'<?php echo "A";$GLOBALS[\n(list($x)=[1])\n]=7;echo "B";'),
 ('key/list-effect/unset', b'<?php echo "A";unset($GLOBALS[\n(list($x)=[1])\n]);echo "B";'),
 ('key/list-effect/quiet', b'<?php echo "A";echo $GLOBALS[\n(list($x)=[1])\n]??7;echo "B";'),
 ('key/list-effect/coalesce-write', b'<?php echo "A";$GLOBALS[\n(list($x)=[1])\n]??=7;echo "B";'),
 ('key/list-effect/reference', b'<?php echo "A";$r=&$GLOBALS[\n(list($x)=[1])\n];echo "B";'),
 ('key/header/read', b'<?php echo "A";echo $GLOBALS[\n"http_response_header"\n];echo "B";'),
 ('key/header/write', b'<?php echo "A";$GLOBALS[\n"http_response_header"\n]=7;echo "B";'),
 ('key/header/unset', b'<?php echo "A";unset($GLOBALS[\n"http_response_header"\n]);echo "B";'),
 ('key/header/quiet', b'<?php echo "A";echo $GLOBALS[\n"http_response_header"\n]??7;echo "B";'),
 ('key/header/coalesce-write', b'<?php echo "A";$GLOBALS[\n"http_response_header"\n]??=7;echo "B";'),
 ('key/header/reference', b'<?php echo "A";$r=&$GLOBALS[\n"http_response_header"\n];echo "B";'),
 ('key/null/read', b'<?php echo "A";echo $GLOBALS[\nnull\n];echo "B";'),
 ('key/null/write', b'<?php echo "A";$GLOBALS[\nnull\n]=7;echo "B";'),
 ('key/null/unset', b'<?php echo "A";unset($GLOBALS[\nnull\n]);echo "B";'),
 ('key/null/quiet', b'<?php echo "A";echo $GLOBALS[\nnull\n]??7;echo "B";'),
 ('key/null/coalesce-write', b'<?php echo "A";$GLOBALS[\nnull\n]??=7;echo "B";'),
 ('key/null/reference', b'<?php echo "A";$r=&$GLOBALS[\nnull\n];echo "B";'),
 ('key/float/read', b'<?php echo "A";echo $GLOBALS[\n1.2\n];echo "B";'),
 ('key/float/write', b'<?php echo "A";$GLOBALS[\n1.2\n]=7;echo "B";'),
 ('key/float/unset', b'<?php echo "A";unset($GLOBALS[\n1.2\n]);echo "B";'),
 ('key/float/quiet', b'<?php echo "A";echo $GLOBALS[\n1.2\n]??7;echo "B";'),
 ('key/float/coalesce-write', b'<?php echo "A";$GLOBALS[\n1.2\n]??=7;echo "B";'),
 ('key/float/reference', b'<?php echo "A";$r=&$GLOBALS[\n1.2\n];echo "B";'),
 ('phase/append-read', b'<?php echo $GLOBALS[];'),
 ('phase/append-write', b'<?php $GLOBALS[]=1;'),
 ('phase/append-quiet', b'<?php echo $GLOBALS[]??1;'),
 ('phase/append-coalesce', b'<?php $GLOBALS[]??=1;'),
 ('phase/append-unset', b'<?php unset($GLOBALS[]);'),
 ('phase/literal-concat-read', b'<?php echo ${"GLO"."BALS"}[[]];'),
 ('phase/literal-concat-quiet', b'<?php echo ${"GLO"."BALS"}[[]]??1;'),
 ('phase/ternary-base-read', b'<?php echo ${true?"GLOBALS":"x"}[[]];'),
 ('phase/ternary-base-write', b'<?php ${true?"GLOBALS":"x"}[[]]=1;'),
 ('phase/global-read-header-flag',
  b'<?php echo $GLOBALS["http_response_header"];echo $http_response_header;'),
 ('phase/global-write-header-flag', b'<?php $GLOBALS["http_response_header"]=1;echo $http_response_header;'),
 ('phase/global-coalesce-header-flag',
  b'<?php $GLOBALS["http_response_header"]??=1;echo $http_response_header;'),
 ('phase/cast-nan-name', b'<?php echo $GLOBALS[(string)NAN];'),
 ('phase/write-hole-priority', b'<?php $GLOBALS[[]]=[,$x];'),
 ('phase/coalesce-hole-priority', b'<?php $GLOBALS[[]]??=[,$x];'),
 ('phase/nested-append-priority', b'<?php echo $GLOBALS[][[]]??1;'),
 ('cv-order/dead-read',
  b'<?php if(false){$b;$a;} $a=1;$b=2; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"||$p'
  b'robe_key==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} '),
 ('cv-order/dead-write',
  b'<?php if(false){$b=0;$a=0;} $a=1;$b=2; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"'
  b'||$probe_key==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} '),
 ('cv-order/dead-dynamic-constant',
  b'<?php if(false){${"b"|""};$a;} $a=1;${"b"|""}=2; foreach($GLOBALS as $probe_key=>$probe_value){if($probe'
  b'_key==="a"||$probe_key==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} '),
 ('cv-order/dead-literal-concat',
  b'<?php if(false){${"b".""};$a;} $a=1;${"b".""}=2; foreach($GLOBALS as $probe_key=>$probe_value){if($probe'
  b'_key==="a"||$probe_key==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} '),
 ('cv-order/dead-ternary-name',
  b'<?php if(false){${true?"b":"b"};$a;} $a=1;${true?"b":"b"}=2; foreach($GLOBALS as $probe_key=>$probe_valu'
  b'e){if($probe_key==="a"||$probe_key==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} '),
 ('cv-order/assignment-order',
  b'<?php if(false){$b=$a;} $a=1;$b=2; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"||$p'
  b'robe_key==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} '),
 ('cv-order/reference-order',
  b'<?php if(false){$b=&$a;} $a=1;$b=2; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"||$'
  b'probe_key==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} '),
 ('cv-order/dim-order',
  b'<?php if(false){$b[$c]=$a;} $a=1;$b=2;$c=3; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key='
  b'=="a"||$probe_key==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} '),
 ('cv-order/list-rhs-order',
  b'<?php if(false){list($b,$c)=$a;} $c=3;$b=2;$a=1; foreach($GLOBALS as $probe_key=>$probe_value){if($probe'
  b'_key==="a"||$probe_key==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} '),
 ('cv-order/list-key-order',
  b'<?php if(false){list($c=>$b)=$a;} $c=3;$b=2;$a=1; foreach($GLOBALS as $probe_key=>$probe_value){if($prob'
  b'e_key==="a"||$probe_key==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} '),
 ('cv-order/foreach-order',
  b'<?php foreach([] as $a=>$b){$c=1;} $a=1;$b=2;$c=3; foreach($GLOBALS as $probe_key=>$probe_value){if($pro'
  b'be_key==="a"||$probe_key==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} '),
 ('cv-order/foreach-iterable-order',
  b'<?php if(false){foreach($c as $a=>$b){}} $a=1;$b=2;$c=3; foreach($GLOBALS as $probe_key=>$probe_value){i'
  b'f($probe_key==="a"||$probe_key==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} '),
 ('cv-order/for-order',
  b'<?php for($a=0;$b??false;$c=0){$d=0;} $a=1;$b=2;$c=3;$d=4; foreach($GLOBALS as $probe_key=>$probe_value)'
  b'{if($probe_key==="a"||$probe_key==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} '),
 ('cv-order/skipped-short-circuit',
  b'<?php false&&$b; $a=1;${"b"|""}=2; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"||$p'
  b'robe_key==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} '),
 ('cv-order/visited-coalesce-rhs',
  b'<?php $a??$b; $a=1;$b=2; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"||$probe_key=='
  b'="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} '),
 ('cv-order/coalesce-assignment',
  b'<?php if(false){$b[$c]??=$a;} $a=1;$b=2;$c=3; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_ke'
  b'y==="a"||$probe_key==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} '),
 ('cv-order/global-key-not-cv',
  b'<?php if(false){$GLOBALS["b"];$a;} $a=1;$GLOBALS["b"]=2; foreach($GLOBALS as $probe_key=>$probe_value){i'
  b'f($probe_key==="a"||$probe_key==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} '),
 ('cv-order/computed-global-name',
  b'<?php ${true?"GLOBALS":"x"}=["b"=>2]; $a=1; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key='
  b'=="a"||$probe_key==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} '),
 ('cv-order/unset-reassign',
  b'<?php $b=2;$a=1;unset($b);$b=3; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"||$prob'
  b'e_key==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} '),
 ('cv-order/dynamic-before-cv',
  b'<?php ${"b"|""}=2;$a=1; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"||$probe_key==='
  b'"b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} '),
 ('cv-special/this-read', b'<?php echo $this;'),
 ('cv-special/this-quiet', b'<?php echo $this??1;'),
 ('cv-special/this-compound', b'<?php $this+=1;'),
 ('cv-special/this-dim', b'<?php echo $this[0];'),
 ('cv-special/this-list', b'<?php list($a)=$this;'),
 ('cv-special/this-list-ref', b'<?php list(&$a)=$this;'),
 ('cv-special/this-list-concat', b'<?php list($a)=${"th"."is"};'),
 ('cv-special/this-list-temp', b'<?php list($a)=${true?"this":"x"};'),
 ('cv-special/autoglobals', b'<?php echo $_GET,$_POST,$_COOKIE,$_REQUEST,$_FILES,$_ENV,$_SERVER,$GLOBALS;'),
 ('cv-special/empty-name', b'<?php ${""}=1; echo ${""};'),
 ('cv-special/numeric-name', b'<?php ${1}=1; ${1.5}=2;'),
 ('cv-special/binary-name', b'<?php ${"a\\0b"}=1;'),
 ('cv-special/autoglobal-dim', b'<?php $GLOBALS["a"]=1; echo $_GET["a"];'),
 ('cv-special/header', b'<?php echo $http_response_header;'),
 ('activation/baseline',
  b'<?php  foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} '),
 ('activation/env',
  b'<?php $_ENV; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} '),
 ('activation/request',
  b'<?php $_REQUEST; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} '),
 ('activation/env-request',
  b'<?php $_ENV;$_REQUEST; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";}'
  b' '),
 ('activation/request-env',
  b'<?php $_REQUEST;$_ENV; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";}'
  b' '),
 ('activation/dead-env',
  b'<?php if(false){$_ENV;} foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";'
  b'} '),
 ('activation/dead-write',
  b'<?php if(false){$_ENV=[];} foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "'
  b'R";} '),
 ('activation/dead-unset',
  b'<?php if(false){unset($_ENV);} foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")ec'
  b'ho "R";} '),
 ('activation/skip-and',
  b'<?php false&&$_ENV; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} '),
 ('activation/skip-or',
  b'<?php true||$_ENV; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} '),
 ('activation/skip-ternary',
  b'<?php true?1:$_ENV; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} '),
 ('activation/visit-ternary',
  b'<?php true?$_ENV:1; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} '),
 ('activation/skip-coalesce',
  b'<?php 1??$_ENV; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} '),
 ('activation/visit-coalesce',
  b'<?php $x??$_ENV; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} '),
 ('activation/literal-concat',
  b'<?php ${"_E"."NV"}; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} '),
 ('activation/computed-ternary',
  b'<?php ${true?"_ENV":"x"}; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R'
  b'";} '),
 ('activation/computed-bitwise',
  b'<?php ${"_ENV"|""}; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} '),
 ('activation/computed-cast',
  b'<?php ${(string)"_ENV"}; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R"'
  b';} '),
 ('activation/runtime-name',
  b'<?php $n="_ENV";$$n; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} '),
 ('activation/global-key',
  b'<?php $GLOBALS["_ENV"]; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";'
  b'} '),
 ('activation/global-key-write',
  b'<?php $GLOBALS["_ENV"]=[]; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "'
  b'R";} '),
 ('activation/global-key-unset',
  b'<?php unset($GLOBALS["_ENV"]); foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")ec'
  b'ho "R";} '),
 ('activation/global-key-coalesce',
  b'<?php $GLOBALS["_ENV"]??=[]; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo'
  b' "R";} '),
 ('activation/env-coalesce',
  b'<?php $_ENV??=[]; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} '),
 ('activation/foreach-dead',
  b'<?php foreach([] as $_ENV){} foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo'
  b' "R";} '),
 ('activation/list-rhs',
  b'<?php if(false){list($a)=$_ENV;} foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")'
  b'echo "R";} '),
 ('activation/list-target',
  b'<?php if(false){list($_ENV)=[];} foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")'
  b'echo "R";} '),
 ('activation/direct-globals',
  b'<?php $GLOBALS; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} '),
 ('activation/list-globals',
  b'<?php if(false){list($a)=$GLOBALS;} foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUES'
  b'T")echo "R";} '),
 ('activation/computed-globals',
  b'<?php ${true?"GLOBALS":"x"}; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo'
  b' "R";} '),
 ('activation/for-order',
  b'<?php for(;$_ENV;){$_REQUEST;break;} foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUE'
  b'ST")echo "R";} '),
 ('activation/duplicate',
  b'<?php $_ENV;$_ENV;$_REQUEST;$_ENV; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST'
  b'")echo "R";} '),
 ('activation/request-before-get-write',
  b'<?php $_GET["x"]=1;echo $_REQUEST["x"]??"missing"; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";i'
  b'f($k==="_REQUEST")echo "R";} ')]

BOUNDARIES = [('cv-order/dead-read',
  b'<?php if(false){$b;$a;} $a=1;$b=2; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"||$probe_key==="b"||$pro'
  b'be_key==="c"||$probe_key==="d")echo $probe_key;} ',
  ['P.CVS = [[98], [97], [112, 114, 111, 98, 101, 95, 118, 97, 108, 117, 101], [112, 114, 111, 98, 101, 95, 107, 101, 121]]']),
 ('cv-order/dead-write',
  b'<?php if(false){$b=0;$a=0;} $a=1;$b=2; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"||$probe_key==="b"||'
  b'$probe_key==="c"||$probe_key==="d")echo $probe_key;} ',
  ['P.CVS = [[98], [97], [112, 114, 111, 98, 101, 95, 118, 97, 108, 117, 101], [112, 114, 111, 98, 101, 95, 107, 101, 121]]']),
 ('cv-order/dead-dynamic-constant',
  b'<?php if(false){${"b"|""};$a;} $a=1;${"b"|""}=2; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"||$probe_k'
  b'ey==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} ',
  ['P.CVS = [[97], [112, 114, 111, 98, 101, 95, 118, 97, 108, 117, 101], [112, 114, 111, 98, 101, 95, 107, 101, 121]]']),
 ('cv-order/dead-literal-concat',
  b'<?php if(false){${"b".""};$a;} $a=1;${"b".""}=2; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"||$probe_k'
  b'ey==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} ',
  ['P.CVS = [[98], [97], [112, 114, 111, 98, 101, 95, 118, 97, 108, 117, 101], [112, 114, 111, 98, 101, 95, 107, 101, 121]]']),
 ('cv-order/dead-ternary-name',
  b'<?php if(false){${true?"b":"b"};$a;} $a=1;${true?"b":"b"}=2; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="'
  b'a"||$probe_key==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} ',
  ['P.CVS = [[97], [112, 114, 111, 98, 101, 95, 118, 97, 108, 117, 101], [112, 114, 111, 98, 101, 95, 107, 101, 121]]']),
 ('cv-order/assignment-order',
  b'<?php if(false){$b=$a;} $a=1;$b=2; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"||$probe_key==="b"||$pro'
  b'be_key==="c"||$probe_key==="d")echo $probe_key;} ',
  ['P.CVS = [[98], [97], [112, 114, 111, 98, 101, 95, 118, 97, 108, 117, 101], [112, 114, 111, 98, 101, 95, 107, 101, 121]]']),
 ('cv-order/reference-order',
  b'<?php if(false){$b=&$a;} $a=1;$b=2; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"||$probe_key==="b"||$pr'
  b'obe_key==="c"||$probe_key==="d")echo $probe_key;} ',
  ['P.CVS = [[98], [97], [112, 114, 111, 98, 101, 95, 118, 97, 108, 117, 101], [112, 114, 111, 98, 101, 95, 107, 101, 121]]']),
 ('cv-order/dim-order',
  b'<?php if(false){$b[$c]=$a;} $a=1;$b=2;$c=3; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"||$probe_key==='
  b'"b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} ',
  ['P.CVS = [[98], [99], [97], [112, 114, 111, 98, 101, 95, 118, 97, 108, 117, 101], [112, 114, 111, 98, 101, 95, 107, 101, '
   '121]]']),
 ('cv-order/list-rhs-order',
  b'<?php if(false){list($b,$c)=$a;} $c=3;$b=2;$a=1; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"||$probe_k'
  b'ey==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} ',
  ['P.CVS = [[97], [98], [99], [112, 114, 111, 98, 101, 95, 118, 97, 108, 117, 101], [112, 114, 111, 98, 101, 95, 107, 101, '
   '121]]']),
 ('cv-order/list-key-order',
  b'<?php if(false){list($c=>$b)=$a;} $c=3;$b=2;$a=1; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"||$probe_'
  b'key==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} ',
  ['P.CVS = [[97], [99], [98], [112, 114, 111, 98, 101, 95, 118, 97, 108, 117, 101], [112, 114, 111, 98, 101, 95, 107, 101, '
   '121]]']),
 ('cv-order/foreach-order',
  b'<?php foreach([] as $a=>$b){$c=1;} $a=1;$b=2;$c=3; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"||$probe'
  b'_key==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} ',
  ['P.CVS = [[98], [97], [99], [112, 114, 111, 98, 101, 95, 118, 97, 108, 117, 101], [112, 114, 111, 98, 101, 95, 107, 101, '
   '121]]']),
 ('cv-order/foreach-iterable-order',
  b'<?php if(false){foreach($c as $a=>$b){}} $a=1;$b=2;$c=3; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"||'
  b'$probe_key==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} ',
  ['P.CVS = [[99], [98], [97], [112, 114, 111, 98, 101, 95, 118, 97, 108, 117, 101], [112, 114, 111, 98, 101, 95, 107, 101, '
   '121]]']),
 ('cv-order/for-order',
  b'<?php for($a=0;$b??false;$c=0){$d=0;} $a=1;$b=2;$c=3;$d=4; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"'
  b'||$probe_key==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} ',
  ['P.CVS = [[97], [100], [99], [98], [112, 114, 111, 98, 101, 95, 118, 97, 108, 117, 101], [112, 114, 111, 98, 101, 95, 107, '
   '101, 121]]']),
 ('cv-order/skipped-short-circuit',
  b'<?php false&&$b; $a=1;${"b"|""}=2; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"||$probe_key==="b"||$pro'
  b'be_key==="c"||$probe_key==="d")echo $probe_key;} ',
  ['P.CVS = [[97], [112, 114, 111, 98, 101, 95, 118, 97, 108, 117, 101], [112, 114, 111, 98, 101, 95, 107, 101, 121]]']),
 ('cv-order/visited-coalesce-rhs',
  b'<?php $a??$b; $a=1;$b=2; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"||$probe_key==="b"||$probe_key==="'
  b'c"||$probe_key==="d")echo $probe_key;} ',
  ['P.CVS = [[97], [98], [112, 114, 111, 98, 101, 95, 118, 97, 108, 117, 101], [112, 114, 111, 98, 101, 95, 107, 101, 121]]']),
 ('cv-order/coalesce-assignment',
  b'<?php if(false){$b[$c]??=$a;} $a=1;$b=2;$c=3; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"||$probe_key='
  b'=="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} ',
  ['P.CVS = [[98], [99], [97], [112, 114, 111, 98, 101, 95, 118, 97, 108, 117, 101], [112, 114, 111, 98, 101, 95, 107, 101, '
   '121]]']),
 ('cv-order/global-key-not-cv',
  b'<?php if(false){$GLOBALS["b"];$a;} $a=1;$GLOBALS["b"]=2; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"||'
  b'$probe_key==="b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} ',
  ['P.CVS = [[97], [112, 114, 111, 98, 101, 95, 118, 97, 108, 117, 101], [112, 114, 111, 98, 101, 95, 107, 101, 121]]']),
 ('cv-order/computed-global-name',
  b'<?php ${true?"GLOBALS":"x"}=["b"=>2]; $a=1; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"||$probe_key==='
  b'"b"||$probe_key==="c"||$probe_key==="d")echo $probe_key;} ',
  ['P.CVS = [[97], [112, 114, 111, 98, 101, 95, 118, 97, 108, 117, 101], [112, 114, 111, 98, 101, 95, 107, 101, 121]]']),
 ('cv-order/unset-reassign',
  b'<?php $b=2;$a=1;unset($b);$b=3; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"||$probe_key==="b"||$probe_'
  b'key==="c"||$probe_key==="d")echo $probe_key;} ',
  ['P.CVS = [[98], [97], [112, 114, 111, 98, 101, 95, 118, 97, 108, 117, 101], [112, 114, 111, 98, 101, 95, 107, 101, 121]]']),
 ('cv-order/dynamic-before-cv',
  b'<?php ${"b"|""}=2;$a=1; foreach($GLOBALS as $probe_key=>$probe_value){if($probe_key==="a"||$probe_key==="b"||$probe_key==="c'
  b'"||$probe_key==="d")echo $probe_key;} ',
  ['P.CVS = [[97], [112, 114, 111, 98, 101, 95, 118, 97, 108, 117, 101], [112, 114, 111, 98, 101, 95, 107, 101, 121]]']),
 ('cv-special/this-read', b'<?php echo $this;', ['P.CVS = []']),
 ('cv-special/this-quiet', b'<?php echo $this??1;', ['P.CVS = []']),
 ('cv-special/this-compound', b'<?php $this+=1;', ['P.CVS = []']),
 ('cv-special/this-dim', b'<?php echo $this[0];', ['P.CVS = []']),
 ('cv-special/this-list', b'<?php list($a)=$this;', ['P.CVS = [[116, 104, 105, 115], [97]]']),
 ('cv-special/this-list-ref', b'<?php list(&$a)=$this;', ['P.CVS = [[97]]']),
 ('cv-special/this-list-concat', b'<?php list($a)=${"th"."is"};', ['P.CVS = [[116, 104, 105, 115], [97]]']),
 ('cv-special/this-list-temp', b'<?php list($a)=${true?"this":"x"};', ['P.CVS = [[97]]']),
 ('cv-special/autoglobals', b'<?php echo $_GET,$_POST,$_COOKIE,$_REQUEST,$_FILES,$_ENV,$_SERVER,$GLOBALS;', ['P.CVS = []']),
 ('cv-special/empty-name', b'<?php ${""}=1; echo ${""};', ['P.CVS = [[]]']),
 ('cv-special/numeric-name', b'<?php ${1}=1; ${1.5}=2;', ['P.CVS = [[49], [49, 46, 53]]']),
 ('cv-special/binary-name', b'<?php ${"a\\0b"}=1;', ['P.CVS = [[97, 0, 98]]']),
 ('cv-special/autoglobal-dim', b'<?php $GLOBALS["a"]=1; echo $_GET["a"];', ['P.CVS = []']),
 ('cv-special/header',
  b'<?php echo $http_response_header;',
  ['P.CVS = [[104, 116, 116, 112, 95, 114, 101, 115, 112, 111, 110, 115, 101, 95, 104, 101, 97, 100, 101, 114]]']),
 ('global-header-write', b'<?php $GLOBALS["http_response_header"]=1;', ['P.CVS = eps', 'P.HEADERASSIGNED = false']),
 ('global-array-key-original',
  b'<?php echo $GLOBALS[[]];',
  ['P.CVS = eps', '$ppmemo_at(P.EXPRESSIONS, [PCINDEX 0, PCFIELD 0, PCINDEX 0, PCFIELD 1]) = ((1, (PARRAY n)))']),
 ('global-memoized-key',
  b'<?php $GLOBALS[[]]??=1;',
  ['P.CVS = eps', '$ppmemo_at(P.EXPRESSIONS, [PCINDEX 0, PCFIELD 0, PCFIELD 0, PCFIELD 1]) = ((1, (PARRAY n)))']),
 ('activation/baseline',
  b'<?php  foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = []']),
 ('activation/env',
  b'<?php $_ENV; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = [[95, 69, 78, 86]]']),
 ('activation/request',
  b'<?php $_REQUEST; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = [[95, 82, 69, 81, 85, 69, 83, 84]]']),
 ('activation/env-request',
  b'<?php $_ENV;$_REQUEST; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = [[95, 69, 78, 86], [95, 82, 69, 81, 85, 69, 83, 84]]']),
 ('activation/request-env',
  b'<?php $_REQUEST;$_ENV; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = [[95, 82, 69, 81, 85, 69, 83, 84], [95, 69, 78, 86]]']),
 ('activation/dead-env',
  b'<?php if(false){$_ENV;} foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = [[95, 69, 78, 86]]']),
 ('activation/dead-write',
  b'<?php if(false){$_ENV=[];} foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = [[95, 69, 78, 86]]']),
 ('activation/dead-unset',
  b'<?php if(false){unset($_ENV);} foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = [[95, 69, 78, 86]]']),
 ('activation/skip-and',
  b'<?php false&&$_ENV; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = []']),
 ('activation/skip-or',
  b'<?php true||$_ENV; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = []']),
 ('activation/skip-ternary',
  b'<?php true?1:$_ENV; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = [[95, 69, 78, 86]]']),
 ('activation/visit-ternary',
  b'<?php true?$_ENV:1; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = [[95, 69, 78, 86]]']),
 ('activation/skip-coalesce',
  b'<?php 1??$_ENV; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = [[95, 69, 78, 86]]']),
 ('activation/visit-coalesce',
  b'<?php $x??$_ENV; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = [[95, 69, 78, 86]]']),
 ('activation/literal-concat',
  b'<?php ${"_E"."NV"}; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = [[95, 69, 78, 86]]']),
 ('activation/computed-ternary',
  b'<?php ${true?"_ENV":"x"}; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = []']),
 ('activation/computed-bitwise',
  b'<?php ${"_ENV"|""}; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = [[95, 69, 78, 86]]']),
 ('activation/computed-cast',
  b'<?php ${(string)"_ENV"}; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = []']),
 ('activation/runtime-name',
  b'<?php $n="_ENV";$$n; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = []']),
 ('activation/global-key',
  b'<?php $GLOBALS["_ENV"]; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = []']),
 ('activation/global-key-write',
  b'<?php $GLOBALS["_ENV"]=[]; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = []']),
 ('activation/global-key-unset',
  b'<?php unset($GLOBALS["_ENV"]); foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = []']),
 ('activation/global-key-coalesce',
  b'<?php $GLOBALS["_ENV"]??=[]; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = []']),
 ('activation/env-coalesce',
  b'<?php $_ENV??=[]; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = [[95, 69, 78, 86]]']),
 ('activation/foreach-dead',
  b'<?php foreach([] as $_ENV){} foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = [[95, 69, 78, 86]]']),
 ('activation/list-rhs',
  b'<?php if(false){list($a)=$_ENV;} foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = [[95, 69, 78, 86]]']),
 ('activation/list-target',
  b'<?php if(false){list($_ENV)=[];} foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = [[95, 69, 78, 86]]']),
 ('activation/direct-globals',
  b'<?php $GLOBALS; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = []']),
 ('activation/list-globals',
  b'<?php if(false){list($a)=$GLOBALS;} foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = [[71, 76, 79, 66, 65, 76, 83]]']),
 ('activation/computed-globals',
  b'<?php ${true?"GLOBALS":"x"}; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = []']),
 ('activation/for-order',
  b'<?php for(;$_ENV;){$_REQUEST;break;} foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = [[95, 82, 69, 81, 85, 69, 83, 84], [95, 69, 78, 86]]']),
 ('activation/duplicate',
  b'<?php $_ENV;$_ENV;$_REQUEST;$_ENV; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")echo "R";} ',
  ['P.AUTOGLOBALS = [[95, 69, 78, 86], [95, 82, 69, 81, 85, 69, 83, 84]]']),
 ('activation/request-before-get-write',
  b'<?php $_GET["x"]=1;echo $_REQUEST["x"]??"missing"; foreach($GLOBALS as $k=>$v){if($k==="_ENV")echo "E";if($k==="_REQUEST")ec'
  b'ho "R";} ',
  ['P.AUTOGLOBALS = [[95, 71, 69, 84], [95, 82, 69, 81, 85, 69, 83, 84]]'])]

SOURCES += [('whole-target/direct/write', b'<?php $GLOBALS=1;'),
 ('whole-target/direct/ref-target', b'<?php $GLOBALS=&$x;'),
 ('whole-target/direct/ref-source', b'<?php $x=&$GLOBALS;'),
 ('whole-target/direct/unset', b'<?php unset($GLOBALS);'),
 ('whole-target/direct/compound', b'<?php $GLOBALS+=1;'),
 ('whole-target/direct/update', b'<?php $GLOBALS++;'),
 ('whole-target/direct/coalesce', b'<?php $GLOBALS??=1;'),
 ('whole-target/direct/list', b'<?php [$GLOBALS]=[1];'),
 ('whole-target/direct/foreach', b'<?php foreach([] as $GLOBALS){}'),
 ('whole-target/direct/dim-write', b'<?php $GLOBALS["x"]=1;'),
 ('whole-target/concat/write', b'<?php ${"GLO"."BALS"}=1;'),
 ('whole-target/concat/ref-target', b'<?php ${"GLO"."BALS"}=&$x;'),
 ('whole-target/concat/ref-source', b'<?php $x=&${"GLO"."BALS"};'),
 ('whole-target/concat/unset', b'<?php unset(${"GLO"."BALS"});'),
 ('whole-target/concat/compound', b'<?php ${"GLO"."BALS"}+=1;'),
 ('whole-target/concat/update', b'<?php ${"GLO"."BALS"}++;'),
 ('whole-target/concat/coalesce', b'<?php ${"GLO"."BALS"}??=1;'),
 ('whole-target/concat/list', b'<?php [${"GLO"."BALS"}]=[1];'),
 ('whole-target/concat/foreach', b'<?php foreach([] as ${"GLO"."BALS"}){}'),
 ('whole-target/concat/dim-write', b'<?php ${"GLO"."BALS"}["x"]=1;'),
 ('whole-target/computed/write', b'<?php ${"GLOBALS"|""}=1;'),
 ('whole-target/computed/ref-target', b'<?php ${"GLOBALS"|""}=&$x;'),
 ('whole-target/computed/ref-source', b'<?php $x=&${"GLOBALS"|""};'),
 ('whole-target/computed/unset', b'<?php unset(${"GLOBALS"|""});'),
 ('whole-target/computed/compound', b'<?php ${"GLOBALS"|""}+=1;'),
 ('whole-target/computed/update', b'<?php ${"GLOBALS"|""}++;'),
 ('whole-target/computed/coalesce', b'<?php ${"GLOBALS"|""}??=1;'),
 ('whole-target/computed/list', b'<?php [${"GLOBALS"|""}]=[1];'),
 ('whole-target/computed/foreach', b'<?php foreach([] as ${"GLOBALS"|""}){}'),
 ('whole-target/computed/dim-write', b'<?php ${"GLOBALS"|""}["x"]=1;'),
 ('whole-target/ternary/write', b'<?php ${true?"GLOBALS":"x"}=1;'),
 ('whole-target/ternary/ref-target', b'<?php ${true?"GLOBALS":"x"}=&$x;'),
 ('whole-target/ternary/ref-source', b'<?php $x=&${true?"GLOBALS":"x"};'),
 ('whole-target/ternary/unset', b'<?php unset(${true?"GLOBALS":"x"});'),
 ('whole-target/ternary/compound', b'<?php ${true?"GLOBALS":"x"}+=1;'),
 ('whole-target/ternary/update', b'<?php ${true?"GLOBALS":"x"}++;'),
 ('whole-target/ternary/coalesce', b'<?php ${true?"GLOBALS":"x"}??=1;'),
 ('whole-target/ternary/list', b'<?php [${true?"GLOBALS":"x"}]=[1];'),
 ('whole-target/ternary/foreach', b'<?php foreach([] as ${true?"GLOBALS":"x"}){}'),
 ('whole-target/ternary/dim-write', b'<?php ${true?"GLOBALS":"x"}["x"]=1;'),
 ('whole-target/this/write', b'<?php ${"th"."is"}=1;'),
 ('whole-target/this/ref-target', b'<?php ${"th"."is"}=&$x;'),
 ('whole-target/this/ref-source', b'<?php $x=&${"th"."is"};'),
 ('whole-target/this/unset', b'<?php unset(${"th"."is"});'),
 ('whole-target/this/compound', b'<?php ${"th"."is"}+=1;'),
 ('whole-target/this/update', b'<?php ${"th"."is"}++;'),
 ('whole-target/this/coalesce', b'<?php ${"th"."is"}??=1;'),
 ('whole-target/this/list', b'<?php [${"th"."is"}]=[1];'),
 ('whole-target/this/foreach', b'<?php foreach([] as ${"th"."is"}){}'),
 ('whole-target/this/dim-write', b'<?php ${"th"."is"}["x"]=1;'),
 ('whole-target/header/write', b'<?php ${"http_response_"."header"}=1;'),
 ('whole-target/header/ref-target', b'<?php ${"http_response_"."header"}=&$x;'),
 ('whole-target/header/ref-source', b'<?php $x=&${"http_response_"."header"};'),
 ('whole-target/header/unset', b'<?php unset(${"http_response_"."header"});'),
 ('whole-target/header/compound', b'<?php ${"http_response_"."header"}+=1;'),
 ('whole-target/header/update', b'<?php ${"http_response_"."header"}++;'),
 ('whole-target/header/coalesce', b'<?php ${"http_response_"."header"}??=1;'),
 ('whole-target/header/list', b'<?php [${"http_response_"."header"}]=[1];'),
 ('whole-target/header/foreach', b'<?php foreach([] as ${"http_response_"."header"}){}'),
 ('whole-target/header/dim-write', b'<?php ${"http_response_"."header"}["x"]=1;'),
 ('whole-target/assign-rhs-error', b'<?php ${"GLO"."BALS"}=[[]=>1];'),
 ('whole-target/assign-prior-error', b'<?php [[]=>1];${"GLO"."BALS"}=1;'),
 ('whole-target/unset-prior-arg', b'<?php unset($a[[[]=>1]],${"GLO"."BALS"});'),
 ('whole-target/unset-next-arg', b'<?php unset(${"GLO"."BALS"},$a[[[]=>1]]);'),
 ('whole-target/ref-source-before-lhs', b'<?php $a[[[]=>1]]=&${"GLO"."BALS"};'),
 ('whole-target/ref-target-before-source', b'<?php ${"GLO"."BALS"}=&$a[[[]=>1]];'),
 ('whole-target/ref-both-globals', b'<?php ${"GLO"."BALS"}=&${"GLO"."BALS"};'),
 ('whole-target/list-key-before-target', b'<?php [[[]=>1]=>${"GLO"."BALS"}]=[1];'),
 ('whole-target/list-rhs-before-target', b'<?php [${"GLO"."BALS"}]=[[]=>1];'),
 ('whole-target/foreach-iterable-before-target', b'<?php foreach([[]=>1] as ${"GLO"."BALS"}){}'),
 ('whole-target/foreach-key-after-value', b'<?php foreach([] as $a[[[]=>1]]=>${"GLO"."BALS"}){}'),
 ('whole-target/foreach-ref-iterable', b'<?php foreach(${"GLO"."BALS"} as &$x){}'),
 ('whole-target/list-ref-source', b'<?php [&$x]=${"GLO"."BALS"};'),
 ('whole-target/skipped-assign', b'<?php false&&(${"GLO"."BALS"}=1);'),
 ('whole-target/ordinary-assigned-dead', b'<?php if(false){${"GLO"."BALS"}=1;}'),
 ('whole-target/multiline-assign', b'<?php \n${"GLO"."BALS"}\n=\n1;'),
 ('whole-target/multiline-unset', b'<?php \nunset(\n${"GLO"."BALS"}\n);'),
 ('whole-target/multiline-ref', b'<?php \n$x\n=&\n${"GLO"."BALS"};')]

def inputs():
    paths=[*compiler.SPECS,Path(__file__),ROOT/'frontend/worker.php',ROOT/'spec/schema.json',
           types.PHP,ROOT/'.tools/php-file.so',ROOT/'_build/default/adapter/main.exe',
           ROOT/'tests/semantics/_build/default/numeric_runner.exe']
    return {'closure':types.syntax_validation.implementation_fingerprint(),
            'direct':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}


def main():
    before=inputs();fixtures=[];records=[];boundaries=[]
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
        with tempfile.TemporaryDirectory(prefix='php-globals-compiler-',dir=ROOT/'.tools') as directory:
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
            fixture=work/'check.watsup';fixture.write_text(PREFIX+'\n'.join(fixtures)+'\ndec $main() : bool\ndef $main() = true\n'+''.join(f'  -- if $case{i}()\n' for i in range(len(fixtures))))
            run=subprocess.run([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),*map(str,compiler.SPECS),str(fixture)],capture_output=True,text=True,timeout=180)
            if run.returncode!=0 or run.stdout.strip()!='true':
                failure=Path(tempfile.mkdtemp(prefix='globals-compiler-failure-',dir=ROOT/'.tools'))
                (failure/'results.json').write_text(json.dumps({'fingerprint':before,'records':records,'boundaries':boundaries,'fixture':fixture.read_text(),'status':run.returncode,'stdout':run.stdout,'stderr':run.stderr},indent=2)+'\n')
                raise AssertionError((str(failure),run.stdout,run.stderr))
    finally:
        frontend.close();adapter.close()
    assert before==inputs(),'inputs changed during GLOBALS compiler checks'
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({'scope':'209 exact GLOBALS/compiler-allocation/activation traces and70 allocation/operand/header/activation controls; source execution tested separately','fingerprint':before,'profile':types.PROFILE,'records':records,'boundaries':boundaries},indent=2)+'\n')
    print('GLOBALS compiler: 209 native lints and70 allocation/operand/header/activation controls passed')

if __name__=='__main__':
    main()
