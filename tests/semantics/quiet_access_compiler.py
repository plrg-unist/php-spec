#!/usr/bin/env python3
"""Header compiler flags, quiet access and constant variable-name conversions."""
import base64,hashlib,json,subprocess,tempfile
from pathlib import Path
import source_compiler as compiler
from source_compiler import types,context
ROOT=Path(__file__).resolve().parents[2]
REPORT=ROOT/'coverage/semantics/quiet-access-compiler.json'

SOURCES = [('header/direct/read', b'<?php echo $http_response_header;'),
 ('header/direct/twice', b'<?php echo $http_response_header;\necho $http_response_header;'),
 ('header/direct/write-read', b'<?php $http_response_header=1;\necho $http_response_header;'),
 ('header/direct/dead-write-read', b'<?php if(false){$http_response_header=1;}\necho $http_response_header;'),
 ('header/direct/read-write-read',
  b'<?php echo $http_response_header;\n$http_response_header=1;\necho $http_response_header;'),
 ('header/direct/unset-read', b'<?php unset($http_response_header);\necho $http_response_header;'),
 ('header/direct/compound-read', b'<?php $http_response_header+=1;\necho $http_response_header;'),
 ('header/direct/reference-read', b'<?php $r=&$http_response_header;\necho $http_response_header;'),
 ('header/direct/list-rhs', b'<?php list($a) =\n$http_response_header;'),
 ('header/direct/foreach-target',
  b'<?php foreach([] as\n$http_response_header){}\necho $http_response_header;'),
 ('header/direct/self-dim', b'<?php $http_response_header[0]=\n$http_response_header;'),
 ('header/direct/quiet-read', b'<?php echo $http_response_header ?? 7;\necho $http_response_header;'),
 ('header/scalar/read', b'<?php echo ${"http_response_header"};'),
 ('header/scalar/twice', b'<?php echo ${"http_response_header"};\necho ${"http_response_header"};'),
 ('header/scalar/write-read', b'<?php ${"http_response_header"}=1;\necho ${"http_response_header"};'),
 ('header/scalar/dead-write-read',
  b'<?php if(false){${"http_response_header"}=1;}\necho ${"http_response_header"};'),
 ('header/scalar/read-write-read',
  b'<?php echo ${"http_response_header"};\n${"http_response_header"}=1;\necho ${"http_response_header"};'),
 ('header/scalar/unset-read', b'<?php unset(${"http_response_header"});\necho ${"http_response_header"};'),
 ('header/scalar/compound-read', b'<?php ${"http_response_header"}+=1;\necho ${"http_response_header"};'),
 ('header/scalar/reference-read', b'<?php $r=&${"http_response_header"};\necho ${"http_response_header"};'),
 ('header/scalar/list-rhs', b'<?php list($a) =\n${"http_response_header"};'),
 ('header/scalar/foreach-target',
  b'<?php foreach([] as\n${"http_response_header"}){}\necho ${"http_response_header"};'),
 ('header/scalar/self-dim', b'<?php ${"http_response_header"}[0]=\n${"http_response_header"};'),
 ('header/scalar/quiet-read', b'<?php echo ${"http_response_header"} ?? 7;\necho ${"http_response_header"};'),
 ('header/concat/read', b'<?php echo ${"http_response_"."header"};'),
 ('header/concat/twice', b'<?php echo ${"http_response_"."header"};\necho ${"http_response_"."header"};'),
 ('header/concat/write-read', b'<?php ${"http_response_"."header"}=1;\necho ${"http_response_"."header"};'),
 ('header/concat/dead-write-read',
  b'<?php if(false){${"http_response_"."header"}=1;}\necho ${"http_response_"."header"};'),
 ('header/concat/read-write-read',
  b'<?php echo ${"http_response_"."header"};\n${"http_response_"."header"}=1;\necho ${"http_response_"."he'
  b'ader"};'),
 ('header/concat/unset-read',
  b'<?php unset(${"http_response_"."header"});\necho ${"http_response_"."header"};'),
 ('header/concat/compound-read',
  b'<?php ${"http_response_"."header"}+=1;\necho ${"http_response_"."header"};'),
 ('header/concat/reference-read',
  b'<?php $r=&${"http_response_"."header"};\necho ${"http_response_"."header"};'),
 ('header/concat/list-rhs', b'<?php list($a) =\n${"http_response_"."header"};'),
 ('header/concat/foreach-target',
  b'<?php foreach([] as\n${"http_response_"."header"}){}\necho ${"http_response_"."header"};'),
 ('header/concat/self-dim', b'<?php ${"http_response_"."header"}[0]=\n${"http_response_"."header"};'),
 ('header/concat/quiet-read',
  b'<?php echo ${"http_response_"."header"} ?? 7;\necho ${"http_response_"."header"};'),
 ('header/concat-parentheses/read', b'<?php echo ${("http_response_"."header")};'),
 ('header/concat-parentheses/twice',
  b'<?php echo ${("http_response_"."header")};\necho ${("http_response_"."header")};'),
 ('header/concat-parentheses/write-read',
  b'<?php ${("http_response_"."header")}=1;\necho ${("http_response_"."header")};'),
 ('header/concat-parentheses/dead-write-read',
  b'<?php if(false){${("http_response_"."header")}=1;}\necho ${("http_response_"."header")};'),
 ('header/concat-parentheses/read-write-read',
  b'<?php echo ${("http_response_"."header")};\n${("http_response_"."header")}=1;\necho ${("http_response_'
  b'"."header")};'),
 ('header/concat-parentheses/unset-read',
  b'<?php unset(${("http_response_"."header")});\necho ${("http_response_"."header")};'),
 ('header/concat-parentheses/compound-read',
  b'<?php ${("http_response_"."header")}+=1;\necho ${("http_response_"."header")};'),
 ('header/concat-parentheses/reference-read',
  b'<?php $r=&${("http_response_"."header")};\necho ${("http_response_"."header")};'),
 ('header/concat-parentheses/list-rhs', b'<?php list($a) =\n${("http_response_"."header")};'),
 ('header/concat-parentheses/foreach-target',
  b'<?php foreach([] as\n${("http_response_"."header")}){}\necho ${("http_response_"."header")};'),
 ('header/concat-parentheses/self-dim',
  b'<?php ${("http_response_"."header")}[0]=\n${("http_response_"."header")};'),
 ('header/concat-parentheses/quiet-read',
  b'<?php echo ${("http_response_"."header")} ?? 7;\necho ${("http_response_"."header")};'),
 ('header/ternary/read', b'<?php echo ${true ? "http_response_header" : "other"};'),
 ('header/ternary/twice',
  b'<?php echo ${true ? "http_response_header" : "other"};\necho ${true ? "http_response_header" : "other'
  b'"};'),
 ('header/ternary/write-read',
  b'<?php ${true ? "http_response_header" : "other"}=1;\necho ${true ? "http_response_header" : "other"};'),
 ('header/ternary/dead-write-read',
  b'<?php if(false){${true ? "http_response_header" : "other"}=1;}\necho ${true ? "http_response_header" : "o'
  b'ther"};'),
 ('header/ternary/read-write-read',
  b'<?php echo ${true ? "http_response_header" : "other"};\n${true ? "http_response_header" : "other"}=1;'
  b'\necho ${true ? "http_response_header" : "other"};'),
 ('header/ternary/unset-read',
  b'<?php unset(${true ? "http_response_header" : "other"});\necho ${true ? "http_response_header" : "other"}'
  b';'),
 ('header/ternary/compound-read',
  b'<?php ${true ? "http_response_header" : "other"}+=1;\necho ${true ? "http_response_header" : "other"};'),
 ('header/ternary/reference-read',
  b'<?php $r=&${true ? "http_response_header" : "other"};\necho ${true ? "http_response_header" : "other"};'),
 ('header/ternary/list-rhs', b'<?php list($a) =\n${true ? "http_response_header" : "other"};'),
 ('header/ternary/foreach-target',
  b'<?php foreach([] as\n${true ? "http_response_header" : "other"}){}\necho ${true ? "http_response_heade'
  b'r" : "other"};'),
 ('header/ternary/self-dim',
  b'<?php ${true ? "http_response_header" : "other"}[0]=\n${true ? "http_response_header" : "other"};'),
 ('header/ternary/quiet-read',
  b'<?php echo ${true ? "http_response_header" : "other"} ?? 7;\necho ${true ? "http_response_header" : "othe'
  b'r"};'),
 ('header/runtime/read', b'<?php $n="http_response_header";\necho $$n;'),
 ('header/runtime/twice', b'<?php $n="http_response_header";\necho $$n;\necho $$n;'),
 ('header/runtime/write-read', b'<?php $n="http_response_header";\n$$n=1;\necho $$n;'),
 ('header/runtime/dead-write-read', b'<?php $n="http_response_header";\nif(false){$$n=1;}\necho $$n;'),
 ('header/runtime/read-write-read', b'<?php $n="http_response_header";\necho $$n;\n$$n=1;\necho $$n;'),
 ('header/runtime/unset-read', b'<?php $n="http_response_header";\nunset($$n);\necho $$n;'),
 ('header/runtime/compound-read', b'<?php $n="http_response_header";\n$$n+=1;\necho $$n;'),
 ('header/runtime/reference-read', b'<?php $n="http_response_header";\n$r=&$$n;\necho $$n;'),
 ('header/runtime/list-rhs', b'<?php $n="http_response_header";\nlist($a) =\n$$n;'),
 ('header/runtime/foreach-target', b'<?php $n="http_response_header";\nforeach([] as\n$$n){}\necho $$n;'),
 ('header/runtime/self-dim', b'<?php $n="http_response_header";\n$$n[0]=\n$$n;'),
 ('header/runtime/quiet-read', b'<?php $n="http_response_header";\necho $$n ?? 7;\necho $$n;'),
 ('header/uppercase/read', b'<?php echo $HTTP_RESPONSE_HEADER;'),
 ('header/uppercase/twice', b'<?php echo $HTTP_RESPONSE_HEADER;\necho $HTTP_RESPONSE_HEADER;'),
 ('header/uppercase/write-read', b'<?php $HTTP_RESPONSE_HEADER=1;\necho $HTTP_RESPONSE_HEADER;'),
 ('header/uppercase/dead-write-read',
  b'<?php if(false){$HTTP_RESPONSE_HEADER=1;}\necho $HTTP_RESPONSE_HEADER;'),
 ('header/uppercase/read-write-read',
  b'<?php echo $HTTP_RESPONSE_HEADER;\n$HTTP_RESPONSE_HEADER=1;\necho $HTTP_RESPONSE_HEADER;'),
 ('header/uppercase/unset-read', b'<?php unset($HTTP_RESPONSE_HEADER);\necho $HTTP_RESPONSE_HEADER;'),
 ('header/uppercase/compound-read', b'<?php $HTTP_RESPONSE_HEADER+=1;\necho $HTTP_RESPONSE_HEADER;'),
 ('header/uppercase/reference-read', b'<?php $r=&$HTTP_RESPONSE_HEADER;\necho $HTTP_RESPONSE_HEADER;'),
 ('header/uppercase/list-rhs', b'<?php list($a) =\n$HTTP_RESPONSE_HEADER;'),
 ('header/uppercase/foreach-target',
  b'<?php foreach([] as\n$HTTP_RESPONSE_HEADER){}\necho $HTTP_RESPONSE_HEADER;'),
 ('header/uppercase/self-dim', b'<?php $HTTP_RESPONSE_HEADER[0]=\n$HTTP_RESPONSE_HEADER;'),
 ('header/uppercase/quiet-read', b'<?php echo $HTTP_RESPONSE_HEADER ?? 7;\necho $HTTP_RESPONSE_HEADER;'),
 ('computed-header/concat-ternary/read', b'<?php echo ${"http_response_".(true ? "header" : "other")};'),
 ('computed-header/concat-ternary/write-read',
  b'<?php ${"http_response_".(true ? "header" : "other")}=1;\necho ${"http_response_".(true ? "header" : "oth'
  b'er")};'),
 ('computed-header/concat-ternary/dead-write-read',
  b'<?php if(false){${"http_response_".(true ? "header" : "other")}=1;}\necho ${"http_response_".(true ? "hea'
  b'der" : "other")};'),
 ('computed-header/concat-ternary/list-rhs',
  b'<?php list($a) =\n${"http_response_".(true ? "header" : "other")};'),
 ('computed-header/concat-unary-ternary/read', b'<?php echo ${"http_response_".(+1 ? "header" : "other")};'),
 ('computed-header/concat-unary-ternary/write-read',
  b'<?php ${"http_response_".(+1 ? "header" : "other")}=1;\necho ${"http_response_".(+1 ? "header" : "other")'
  b'};'),
 ('computed-header/concat-unary-ternary/dead-write-read',
  b'<?php if(false){${"http_response_".(+1 ? "header" : "other")}=1;}\necho ${"http_response_".(+1 ? "header"'
  b' : "other")};'),
 ('computed-header/concat-unary-ternary/list-rhs',
  b'<?php list($a) =\n${"http_response_".(+1 ? "header" : "other")};'),
 ('computed-header/constant-dim/read', b'<?php echo ${["http_response_header"][0]};'),
 ('computed-header/constant-dim/write-read',
  b'<?php ${["http_response_header"][0]}=1;\necho ${["http_response_header"][0]};'),
 ('computed-header/constant-dim/dead-write-read',
  b'<?php if(false){${["http_response_header"][0]}=1;}\necho ${["http_response_header"][0]};'),
 ('computed-header/constant-dim/list-rhs', b'<?php list($a) =\n${["http_response_header"][0]};'),
 ('computed-header/cast-string/read', b'<?php echo ${(string) "http_response_header"};'),
 ('computed-header/cast-string/write-read',
  b'<?php ${(string) "http_response_header"}=1;\necho ${(string) "http_response_header"};'),
 ('computed-header/cast-string/dead-write-read',
  b'<?php if(false){${(string) "http_response_header"}=1;}\necho ${(string) "http_response_header"};'),
 ('computed-header/cast-string/list-rhs', b'<?php list($a) =\n${(string) "http_response_header"};'),
 ('computed-header/coalesce/read', b'<?php echo ${"http_response_header" ?? "other"};'),
 ('computed-header/coalesce/write-read',
  b'<?php ${"http_response_header" ?? "other"}=1;\necho ${"http_response_header" ?? "other"};'),
 ('computed-header/coalesce/dead-write-read',
  b'<?php if(false){${"http_response_header" ?? "other"}=1;}\necho ${"http_response_header" ?? "other"};'),
 ('computed-header/coalesce/list-rhs', b'<?php list($a) =\n${"http_response_header" ?? "other"};'),
 ('computed-header/effect-list/read', b'<?php echo ${(list($x)=["http_response_header"])[0]};'),
 ('computed-header/effect-list/write-read',
  b'<?php ${(list($x)=["http_response_header"])[0]}=1;\necho ${(list($x)=["http_response_header"])[0]};'),
 ('computed-header/effect-list/dead-write-read',
  b'<?php if(false){${(list($x)=["http_response_header"])[0]}=1;}\necho ${(list($x)=["http_response_header"])'
  b'[0]};'),
 ('computed-header/effect-list/list-rhs', b'<?php list($a) =\n${(list($x)=["http_response_header"])[0]};'),
 ('known-header/string-or/read', b'<?php echo ${"http_response_header" | ""};'),
 ('known-header/string-or/write-read',
  b'<?php ${"http_response_header" | ""}=1;\necho ${"http_response_header" | ""};'),
 ('known-header/string-or/list-rhs', b'<?php list($a) =\n${"http_response_header" | ""};'),
 ('known-header/string-or/direct-write-read',
  b'<?php $http_response_header=1;\necho ${"http_response_header" | ""};'),
 ('known-header/double-bitnot/read', b'<?php echo ${~~"http_response_header"};'),
 ('known-header/double-bitnot/write-read',
  b'<?php ${~~"http_response_header"}=1;\necho ${~~"http_response_header"};'),
 ('known-header/double-bitnot/list-rhs', b'<?php list($a) =\n${~~"http_response_header"};'),
 ('known-header/double-bitnot/direct-write-read',
  b'<?php $http_response_header=1;\necho ${~~"http_response_header"};'),
 ('known-header/string-and/read', b'<?php echo ${"http_response_header" & "http_response_header"};'),
 ('known-header/string-and/write-read',
  b'<?php ${"http_response_header" & "http_response_header"}=1;\necho ${"http_response_header" & "http_respon'
  b'se_header"};'),
 ('known-header/string-and/list-rhs',
  b'<?php list($a) =\n${"http_response_header" & "http_response_header"};'),
 ('known-header/string-and/direct-write-read',
  b'<?php $http_response_header=1;\necho ${"http_response_header" & "http_response_header"};'),
 ('quiet/coalesce-null-null', b'<?php $a=null;$k=null;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-null-false', b'<?php $a=null;$k=false;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-null-true', b'<?php $a=null;$k=true;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-null-0', b'<?php $a=null;$k=0;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-null--1', b'<?php $a=null;$k=-1;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-null-99', b'<?php $a=null;$k=99;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-null-1.5', b'<?php $a=null;$k=1.5;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-null-NAN', b'<?php $a=null;$k=NAN;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-null-"0x"', b'<?php $a=null;$k="0x";echo $a[$k] ?? 9;'),
 ('quiet/coalesce-null-" 0"', b'<?php $a=null;$k=" 0";echo $a[$k] ?? 9;'),
 ('quiet/coalesce-null-[]', b'<?php $a=null;$k=[];echo $a[$k] ?? 9;'),
 ('quiet/coalesce-false-null', b'<?php $a=false;$k=null;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-false-false', b'<?php $a=false;$k=false;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-false-true', b'<?php $a=false;$k=true;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-false-0', b'<?php $a=false;$k=0;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-false--1', b'<?php $a=false;$k=-1;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-false-99', b'<?php $a=false;$k=99;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-false-1.5', b'<?php $a=false;$k=1.5;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-false-NAN', b'<?php $a=false;$k=NAN;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-false-"0x"', b'<?php $a=false;$k="0x";echo $a[$k] ?? 9;'),
 ('quiet/coalesce-false-" 0"', b'<?php $a=false;$k=" 0";echo $a[$k] ?? 9;'),
 ('quiet/coalesce-false-[]', b'<?php $a=false;$k=[];echo $a[$k] ?? 9;'),
 ('quiet/coalesce-true-null', b'<?php $a=true;$k=null;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-true-false', b'<?php $a=true;$k=false;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-true-true', b'<?php $a=true;$k=true;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-true-0', b'<?php $a=true;$k=0;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-true--1', b'<?php $a=true;$k=-1;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-true-99', b'<?php $a=true;$k=99;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-true-1.5', b'<?php $a=true;$k=1.5;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-true-NAN', b'<?php $a=true;$k=NAN;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-true-"0x"', b'<?php $a=true;$k="0x";echo $a[$k] ?? 9;'),
 ('quiet/coalesce-true-" 0"', b'<?php $a=true;$k=" 0";echo $a[$k] ?? 9;'),
 ('quiet/coalesce-true-[]', b'<?php $a=true;$k=[];echo $a[$k] ?? 9;'),
 ('quiet/coalesce-7-null', b'<?php $a=7;$k=null;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-7-false', b'<?php $a=7;$k=false;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-7-true', b'<?php $a=7;$k=true;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-7-0', b'<?php $a=7;$k=0;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-7--1', b'<?php $a=7;$k=-1;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-7-99', b'<?php $a=7;$k=99;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-7-1.5', b'<?php $a=7;$k=1.5;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-7-NAN', b'<?php $a=7;$k=NAN;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-7-"0x"', b'<?php $a=7;$k="0x";echo $a[$k] ?? 9;'),
 ('quiet/coalesce-7-" 0"', b'<?php $a=7;$k=" 0";echo $a[$k] ?? 9;'),
 ('quiet/coalesce-7-[]', b'<?php $a=7;$k=[];echo $a[$k] ?? 9;'),
 ('quiet/coalesce-"ab"-null', b'<?php $a="ab";$k=null;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-"ab"-false', b'<?php $a="ab";$k=false;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-"ab"-true', b'<?php $a="ab";$k=true;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-"ab"-0', b'<?php $a="ab";$k=0;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-"ab"--1', b'<?php $a="ab";$k=-1;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-"ab"-99', b'<?php $a="ab";$k=99;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-"ab"-1.5', b'<?php $a="ab";$k=1.5;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-"ab"-NAN', b'<?php $a="ab";$k=NAN;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-"ab"-"0x"', b'<?php $a="ab";$k="0x";echo $a[$k] ?? 9;'),
 ('quiet/coalesce-"ab"-" 0"', b'<?php $a="ab";$k=" 0";echo $a[$k] ?? 9;'),
 ('quiet/coalesce-"ab"-[]', b'<?php $a="ab";$k=[];echo $a[$k] ?? 9;'),
 ('quiet/coalesce-[]-null', b'<?php $a=[];$k=null;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-[]-false', b'<?php $a=[];$k=false;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-[]-true', b'<?php $a=[];$k=true;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-[]-0', b'<?php $a=[];$k=0;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-[]--1', b'<?php $a=[];$k=-1;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-[]-99', b'<?php $a=[];$k=99;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-[]-1.5', b'<?php $a=[];$k=1.5;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-[]-NAN', b'<?php $a=[];$k=NAN;echo $a[$k] ?? 9;'),
 ('quiet/coalesce-[]-"0x"', b'<?php $a=[];$k="0x";echo $a[$k] ?? 9;'),
 ('quiet/coalesce-[]-" 0"', b'<?php $a=[];$k=" 0";echo $a[$k] ?? 9;'),
 ('quiet/coalesce-[]-[]', b'<?php $a=[];$k=[];echo $a[$k] ?? 9;'),
 ('phase/literal-array', b'<?php echo [1][0] ?? 7;'),
 ('phase/array-union', b'<?php echo ([1]+[2])[0] ?? 7;'),
 ('phase/string-key', b'<?php echo "abc"["0x"] ?? 7;'),
 ('phase/string-float', b'<?php echo "abc"[1.5] ?? 7;'),
 ('phase/string-array', b'<?php echo "abc"[[]] ?? 7;'),
 ('phase/null-base', b'<?php echo null[[]] ?? 7;'),
 ('phase/false-base', b'<?php echo (false)[0] ?? 7;'),
 ('phase/int-base', b'<?php echo (1)[0] ?? 7;'),
 ('phase/float-base', b'<?php echo (1.2)[0] ?? 7;'),
 ('phase/missing-base', b'<?php echo $a[0] ?? 7;'),
 ('phase/nested-missing', b'<?php echo $a[0][1] ?? 7;'),
 ('phase/empty-key', b'<?php echo $a[] ?? 7;'),
 ('phase/nested-empty-key', b'<?php echo $a[0][] ?? 7;'),
 ('phase/literal-empty-key', b'<?php echo [1][] ?? 7;'),
 ('phase/null-empty-key', b'<?php echo null[] ?? 7;'),
 ('phase/right-hole', b'<?php echo [1][0] ?? [,$x];'),
 ('phase/prepass-selected', b'<?php echo [[1][0] ?? [,$x]];'),
 ('phase/prepass-nonconstant', b'<?php $u=1;echo [$u,[1][0] ?? [,$x]];'),
 ('phase/known-effect-right-hole', b'<?php echo (list($x)=[1]) ?? [,$x];'),
 ('phase/quiet-header-state', b'<?php echo $http_response_header ?? 7;echo $http_response_header;'),
 ('phase/quiet-cv-key-line', b'<?php echo $a[\n$k] ?? 7;'),
 ('phase/quiet-temp-key-line', b'<?php echo $a[1.2+\n0] ?? 7;'),
 ('phase/quiet-computed-name', b'<?php echo ${"".\n$n} ?? 7;'),
 ('phase/quiet-computed-this', b'<?php $n="this"; echo $$n ?? 7;'),
 ('name/empty-array/read', b'<?php echo "A";echo ${\n[]\n};echo "B";'),
 ('name/empty-array/write', b'<?php echo "A";${\n[]\n}=7;echo "B";'),
 ('name/empty-array/unset', b'<?php echo "A";unset(${\n[]\n});echo "B";'),
 ('name/empty-array/quiet', b'<?php echo "A";echo ${\n[]\n}??7;echo "B";'),
 ('name/empty-array/reference', b'<?php echo "A";$r=&${\n[]\n};echo "B";'),
 ('name/array/read', b'<?php echo "A";echo ${\n[1]\n};echo "B";'),
 ('name/array/write', b'<?php echo "A";${\n[1]\n}=7;echo "B";'),
 ('name/array/unset', b'<?php echo "A";unset(${\n[1]\n});echo "B";'),
 ('name/array/quiet', b'<?php echo "A";echo ${\n[1]\n}??7;echo "B";'),
 ('name/array/reference', b'<?php echo "A";$r=&${\n[1]\n};echo "B";'),
 ('name/nan/read', b'<?php echo "A";echo ${\nNAN\n};echo "B";'),
 ('name/nan/write', b'<?php echo "A";${\nNAN\n}=7;echo "B";'),
 ('name/nan/unset', b'<?php echo "A";unset(${\nNAN\n});echo "B";'),
 ('name/nan/quiet', b'<?php echo "A";echo ${\nNAN\n}??7;echo "B";'),
 ('name/nan/reference', b'<?php echo "A";$r=&${\nNAN\n};echo "B";'),
 ('name/infinity/read', b'<?php echo "A";echo ${\nINF\n};echo "B";'),
 ('name/infinity/write', b'<?php echo "A";${\nINF\n}=7;echo "B";'),
 ('name/infinity/unset', b'<?php echo "A";unset(${\nINF\n});echo "B";'),
 ('name/infinity/quiet', b'<?php echo "A";echo ${\nINF\n}??7;echo "B";'),
 ('name/infinity/reference', b'<?php echo "A";$r=&${\nINF\n};echo "B";'),
 ('name/list-effect/read', b'<?php echo "A";echo ${\n(list($x)=[1])\n};echo "B";'),
 ('name/list-effect/write', b'<?php echo "A";${\n(list($x)=[1])\n}=7;echo "B";'),
 ('name/list-effect/unset', b'<?php echo "A";unset(${\n(list($x)=[1])\n});echo "B";'),
 ('name/list-effect/quiet', b'<?php echo "A";echo ${\n(list($x)=[1])\n}??7;echo "B";'),
 ('name/list-effect/reference', b'<?php echo "A";$r=&${\n(list($x)=[1])\n};echo "B";'),
 ('name/list-nested-effect/read', b'<?php echo "A";echo ${\n(list($x)=[[1]])\n};echo "B";'),
 ('name/list-nested-effect/write', b'<?php echo "A";${\n(list($x)=[[1]])\n}=7;echo "B";'),
 ('name/list-nested-effect/unset', b'<?php echo "A";unset(${\n(list($x)=[[1]])\n});echo "B";'),
 ('name/list-nested-effect/quiet', b'<?php echo "A";echo ${\n(list($x)=[[1]])\n}??7;echo "B";'),
 ('name/list-nested-effect/reference', b'<?php echo "A";$r=&${\n(list($x)=[[1]])\n};echo "B";')]

# Compiler state and occurrence descriptors remain distinct from runtime values.
BOUNDARIES = [
    ('direct-write', b'<?php $http_response_header=1;', ['P.HEADERASSIGNED = true']),
    ('dead-write', b'<?php if(false){$http_response_header=1;} echo $http_response_header;', ['P.HEADERASSIGNED = true']),
    ('read-only', b'<?php echo $http_response_header;', ['P.HEADERASSIGNED = false']),
    ('unset-only', b'<?php unset($http_response_header);', ['P.HEADERASSIGNED = false']),
    ('quiet-only', b'<?php echo $http_response_header??1;', ['P.HEADERASSIGNED = false', '$ppaccess(P, [PCINDEX 0, PCFIELD 0, PCINDEX 0, PCFIELD 0]) = (PPIS)']),
    ('read-write', b'<?php $http_response_header+=1;', ['P.HEADERASSIGNED = false']),
    ('computed-write', b'<?php ${"http_response_heade"|"http_response_header"}=1;', ['P.HEADERASSIGNED = false']),
    ('literal-concat-write', b'<?php ${"http_response_"."header"}=1;', ['P.HEADERASSIGNED = true']),
    ('quiet-dimension-key', b'<?php echo $a[$k]??1;', ['$ppaccess(P, [PCINDEX 0, PCFIELD 0, PCINDEX 0, PCFIELD 0]) = (PPIS)', '$ppaccess(P, [PCINDEX 0, PCFIELD 0, PCINDEX 0, PCFIELD 0, PCFIELD 0]) = (PPIS)', '$ppaccess(P, [PCINDEX 0, PCFIELD 0, PCINDEX 0, PCFIELD 0, PCFIELD 1]) = (PPR)']),
    ('quiet-temporary-base', b'<?php echo [1][0]??1;', ['$ppaccess(P, [PCINDEX 0, PCFIELD 0, PCINDEX 0, PCFIELD 0, PCFIELD 0]) = (PPR)']),
    ('original-array-name', b'<?php echo ${[]};', ['$ppconstants(P) = PPCCONSTANTS (pcpath_constants, pvalue_constants)*', '$ppconstant_at((pcpath_constants, pvalue_constants)*, [PCINDEX 0, PCFIELD 0, PCINDEX 0, PCFIELD 0]) = (PARRAY n_array)']),
    ('effectful-array-name', b'<?php echo ${(list($x)=[[1]])};', ['$ppconstants(P) = PPCCONSTANTS (pcpath_constants, pvalue_constants)*', '$ppconstant_at((pcpath_constants, pvalue_constants)*, [PCINDEX 0, PCFIELD 0, PCINDEX 0, PCFIELD 0]) = (PARRAY n_array)', '$quiet_effect(P.EXPRESSIONS, [PCINDEX 0, PCFIELD 0, PCINDEX 0, PCFIELD 0])']),
]

PREFIX = compiler.PREFIX + r"""
dec $quiet_effect(ppexprdone*, pcpath) : bool
def $quiet_effect(eps, pcpath) = false
def $quiet_effect((PPCEFFECT pcpath) :: ppexprdone*, pcpath) = true
def $quiet_effect((PPCEFFECT pcpath_other) :: ppexprdone*, pcpath) = $quiet_effect(ppexprdone*, pcpath)
  -- if pcpath_other =/= pcpath
def $quiet_effect((PPCEXPR pcpath_other n pvalue?) :: ppexprdone*, pcpath) = $quiet_effect(ppexprdone*, pcpath)
"""

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
        with tempfile.TemporaryDirectory(prefix='php-quiet-compiler-',dir=ROOT/'.tools') as directory:
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
                failure=Path(tempfile.mkdtemp(prefix='quiet-compiler-failure-',dir=ROOT/'.tools'))
                (failure/'results.json').write_text(json.dumps({'fingerprint':before,'records':records,'boundaries':boundaries,'fixture':fixture.read_text(),'status':run.returncode,'stdout':run.stdout,'stderr':run.stderr},indent=2)+'\n')
                raise AssertionError((str(failure),run.stdout,run.stderr))
    finally:
        frontend.close();adapter.close()
    assert before==inputs(),'inputs changed during quiet compiler checks'
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({'scope':'240 exact header/name/quiet compiler traces and12 compiler state/access/operand controls; source execution tested separately','fingerprint':before,'profile':types.PROFILE,'records':records,'boundaries':boundaries},indent=2)+'\n')
    print('Quiet compiler: 240 native lints and12 compiler state/access controls passed')

if __name__=='__main__':
    main()
