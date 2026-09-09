#!/usr/bin/env python3
"""Terminal isset/empty: exact source outcomes, effects and ownership."""
from pathlib import Path
import base64,hashlib,json,re,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[2];D=ROOT;R=ROOT
sys.path.insert(0,str(R/'tests/semantics'));import static_types as t;import destructuring as d;import foreach as f

CASES = {'isset-scalar': b'<?php echo isset(1);',
 'isset-array-error': b'<?php echo isset([[]=>1]);',
 'isset-call': b'<?php echo isset(foo([[]=>1]));',
 'isset-method': b'<?php echo isset($x->foo([[]=>1]));',
 'isset-list-effect': b'<?php echo isset((list($a)=[1]));',
 'isset-globals': b'<?php echo isset($GLOBALS);',
 'empty-globals': b'<?php echo empty($GLOBALS);',
 'isset-globals-concat': b'<?php echo isset(${"GLO"."BALS"});',
 'empty-globals-concat': b'<?php echo empty(${"GLO"."BALS"});',
 'isset-globals-hole': b'<?php isset($GLOBALS)||[,$x];',
 'empty-globals-hole': b'<?php empty($GLOBALS)&&[,$x];',
 'isset-globals-prepass': b'<?php [isset($GLOBALS),,];',
 'empty-globals-prepass': b'<?php [empty($GLOBALS),,];',
 'isset-multi-globals': b'<?php echo isset($GLOBALS,$GLOBALS);',
 'isset-multi-missing': b'<?php echo isset($missing,$a[$k++]);echo $k;',
 'isset-multi-invalid': b'<?php echo isset($missing,foo());',
 'isset-multi-global-invalid': b'<?php echo isset($GLOBALS,1);',
 'isset-multi-key-error': b'<?php echo isset($missing,$a[[[]=>1]]);',
 'empty-scalar': b'<?php echo empty(1);',
 'empty-array-error': b'<?php echo empty([[]=>1]);',
 'empty-literal': b'<?php echo empty([]);',
 'empty-nan': b'<?php echo empty(NAN);',
 'empty-list-effect': b'<?php echo empty((list($a)=[1]));echo $a;',
 'empty-list-selected': b'<?php empty((list($a)=[]))||[,$x];',
 'empty-list-unselected': b'<?php empty((list($a)=[1]))||[,$x];',
 'isset-global-empty-key': b'<?php echo isset($GLOBALS[]);',
 'empty-global-empty-key': b'<?php echo empty($GLOBALS[]);',
 'isset-header': b'<?php echo isset($http_response_header);echo $http_response_header;',
 'empty-header': b'<?php echo empty($http_response_header);echo $http_response_header;',
 'isset-name-array': b'<?php echo isset(${[]});',
 'empty-name-array': b'<?php echo empty(${[]});',
 'isset-lines': b'<?php echo isset(\n1\n);',
 'empty-lines': b'<?php echo empty(\n[[]=>1]\n);',
 'isset-null-null': b'<?php $a=null;$k=null;echo isset($a[$k]);',
 'empty-null-null': b'<?php $a=null;$k=null;echo empty($a[$k]);',
 'isset-null-false': b'<?php $a=null;$k=false;echo isset($a[$k]);',
 'empty-null-false': b'<?php $a=null;$k=false;echo empty($a[$k]);',
 'isset-null-true': b'<?php $a=null;$k=true;echo isset($a[$k]);',
 'empty-null-true': b'<?php $a=null;$k=true;echo empty($a[$k]);',
 'isset-null-0': b'<?php $a=null;$k=0;echo isset($a[$k]);',
 'empty-null-0': b'<?php $a=null;$k=0;echo empty($a[$k]);',
 'isset-null--1': b'<?php $a=null;$k=-1;echo isset($a[$k]);',
 'empty-null--1': b'<?php $a=null;$k=-1;echo empty($a[$k]);',
 'isset-null-99': b'<?php $a=null;$k=99;echo isset($a[$k]);',
 'empty-null-99': b'<?php $a=null;$k=99;echo empty($a[$k]);',
 'isset-null-1.5': b'<?php $a=null;$k=1.5;echo isset($a[$k]);',
 'empty-null-1.5': b'<?php $a=null;$k=1.5;echo empty($a[$k]);',
 'isset-null-NAN': b'<?php $a=null;$k=NAN;echo isset($a[$k]);',
 'empty-null-NAN': b'<?php $a=null;$k=NAN;echo empty($a[$k]);',
 'isset-null-"0x"': b'<?php $a=null;$k="0x";echo isset($a[$k]);',
 'empty-null-"0x"': b'<?php $a=null;$k="0x";echo empty($a[$k]);',
 'isset-null-" 0"': b'<?php $a=null;$k=" 0";echo isset($a[$k]);',
 'empty-null-" 0"': b'<?php $a=null;$k=" 0";echo empty($a[$k]);',
 'isset-null-[]': b'<?php $a=null;$k=[];echo isset($a[$k]);',
 'empty-null-[]': b'<?php $a=null;$k=[];echo empty($a[$k]);',
 'isset-false-null': b'<?php $a=false;$k=null;echo isset($a[$k]);',
 'empty-false-null': b'<?php $a=false;$k=null;echo empty($a[$k]);',
 'isset-false-false': b'<?php $a=false;$k=false;echo isset($a[$k]);',
 'empty-false-false': b'<?php $a=false;$k=false;echo empty($a[$k]);',
 'isset-false-true': b'<?php $a=false;$k=true;echo isset($a[$k]);',
 'empty-false-true': b'<?php $a=false;$k=true;echo empty($a[$k]);',
 'isset-false-0': b'<?php $a=false;$k=0;echo isset($a[$k]);',
 'empty-false-0': b'<?php $a=false;$k=0;echo empty($a[$k]);',
 'isset-false--1': b'<?php $a=false;$k=-1;echo isset($a[$k]);',
 'empty-false--1': b'<?php $a=false;$k=-1;echo empty($a[$k]);',
 'isset-false-99': b'<?php $a=false;$k=99;echo isset($a[$k]);',
 'empty-false-99': b'<?php $a=false;$k=99;echo empty($a[$k]);',
 'isset-false-1.5': b'<?php $a=false;$k=1.5;echo isset($a[$k]);',
 'empty-false-1.5': b'<?php $a=false;$k=1.5;echo empty($a[$k]);',
 'isset-false-NAN': b'<?php $a=false;$k=NAN;echo isset($a[$k]);',
 'empty-false-NAN': b'<?php $a=false;$k=NAN;echo empty($a[$k]);',
 'isset-false-"0x"': b'<?php $a=false;$k="0x";echo isset($a[$k]);',
 'empty-false-"0x"': b'<?php $a=false;$k="0x";echo empty($a[$k]);',
 'isset-false-" 0"': b'<?php $a=false;$k=" 0";echo isset($a[$k]);',
 'empty-false-" 0"': b'<?php $a=false;$k=" 0";echo empty($a[$k]);',
 'isset-false-[]': b'<?php $a=false;$k=[];echo isset($a[$k]);',
 'empty-false-[]': b'<?php $a=false;$k=[];echo empty($a[$k]);',
 'isset-true-null': b'<?php $a=true;$k=null;echo isset($a[$k]);',
 'empty-true-null': b'<?php $a=true;$k=null;echo empty($a[$k]);',
 'isset-true-false': b'<?php $a=true;$k=false;echo isset($a[$k]);',
 'empty-true-false': b'<?php $a=true;$k=false;echo empty($a[$k]);',
 'isset-true-true': b'<?php $a=true;$k=true;echo isset($a[$k]);',
 'empty-true-true': b'<?php $a=true;$k=true;echo empty($a[$k]);',
 'isset-true-0': b'<?php $a=true;$k=0;echo isset($a[$k]);',
 'empty-true-0': b'<?php $a=true;$k=0;echo empty($a[$k]);',
 'isset-true--1': b'<?php $a=true;$k=-1;echo isset($a[$k]);',
 'empty-true--1': b'<?php $a=true;$k=-1;echo empty($a[$k]);',
 'isset-true-99': b'<?php $a=true;$k=99;echo isset($a[$k]);',
 'empty-true-99': b'<?php $a=true;$k=99;echo empty($a[$k]);',
 'isset-true-1.5': b'<?php $a=true;$k=1.5;echo isset($a[$k]);',
 'empty-true-1.5': b'<?php $a=true;$k=1.5;echo empty($a[$k]);',
 'isset-true-NAN': b'<?php $a=true;$k=NAN;echo isset($a[$k]);',
 'empty-true-NAN': b'<?php $a=true;$k=NAN;echo empty($a[$k]);',
 'isset-true-"0x"': b'<?php $a=true;$k="0x";echo isset($a[$k]);',
 'empty-true-"0x"': b'<?php $a=true;$k="0x";echo empty($a[$k]);',
 'isset-true-" 0"': b'<?php $a=true;$k=" 0";echo isset($a[$k]);',
 'empty-true-" 0"': b'<?php $a=true;$k=" 0";echo empty($a[$k]);',
 'isset-true-[]': b'<?php $a=true;$k=[];echo isset($a[$k]);',
 'empty-true-[]': b'<?php $a=true;$k=[];echo empty($a[$k]);',
 'isset-7-null': b'<?php $a=7;$k=null;echo isset($a[$k]);',
 'empty-7-null': b'<?php $a=7;$k=null;echo empty($a[$k]);',
 'isset-7-false': b'<?php $a=7;$k=false;echo isset($a[$k]);',
 'empty-7-false': b'<?php $a=7;$k=false;echo empty($a[$k]);',
 'isset-7-true': b'<?php $a=7;$k=true;echo isset($a[$k]);',
 'empty-7-true': b'<?php $a=7;$k=true;echo empty($a[$k]);',
 'isset-7-0': b'<?php $a=7;$k=0;echo isset($a[$k]);',
 'empty-7-0': b'<?php $a=7;$k=0;echo empty($a[$k]);',
 'isset-7--1': b'<?php $a=7;$k=-1;echo isset($a[$k]);',
 'empty-7--1': b'<?php $a=7;$k=-1;echo empty($a[$k]);',
 'isset-7-99': b'<?php $a=7;$k=99;echo isset($a[$k]);',
 'empty-7-99': b'<?php $a=7;$k=99;echo empty($a[$k]);',
 'isset-7-1.5': b'<?php $a=7;$k=1.5;echo isset($a[$k]);',
 'empty-7-1.5': b'<?php $a=7;$k=1.5;echo empty($a[$k]);',
 'isset-7-NAN': b'<?php $a=7;$k=NAN;echo isset($a[$k]);',
 'empty-7-NAN': b'<?php $a=7;$k=NAN;echo empty($a[$k]);',
 'isset-7-"0x"': b'<?php $a=7;$k="0x";echo isset($a[$k]);',
 'empty-7-"0x"': b'<?php $a=7;$k="0x";echo empty($a[$k]);',
 'isset-7-" 0"': b'<?php $a=7;$k=" 0";echo isset($a[$k]);',
 'empty-7-" 0"': b'<?php $a=7;$k=" 0";echo empty($a[$k]);',
 'isset-7-[]': b'<?php $a=7;$k=[];echo isset($a[$k]);',
 'empty-7-[]': b'<?php $a=7;$k=[];echo empty($a[$k]);',
 'isset-"ab"-null': b'<?php $a="ab";$k=null;echo isset($a[$k]);',
 'empty-"ab"-null': b'<?php $a="ab";$k=null;echo empty($a[$k]);',
 'isset-"ab"-false': b'<?php $a="ab";$k=false;echo isset($a[$k]);',
 'empty-"ab"-false': b'<?php $a="ab";$k=false;echo empty($a[$k]);',
 'isset-"ab"-true': b'<?php $a="ab";$k=true;echo isset($a[$k]);',
 'empty-"ab"-true': b'<?php $a="ab";$k=true;echo empty($a[$k]);',
 'isset-"ab"-0': b'<?php $a="ab";$k=0;echo isset($a[$k]);',
 'empty-"ab"-0': b'<?php $a="ab";$k=0;echo empty($a[$k]);',
 'isset-"ab"--1': b'<?php $a="ab";$k=-1;echo isset($a[$k]);',
 'empty-"ab"--1': b'<?php $a="ab";$k=-1;echo empty($a[$k]);',
 'isset-"ab"-99': b'<?php $a="ab";$k=99;echo isset($a[$k]);',
 'empty-"ab"-99': b'<?php $a="ab";$k=99;echo empty($a[$k]);',
 'isset-"ab"-1.5': b'<?php $a="ab";$k=1.5;echo isset($a[$k]);',
 'empty-"ab"-1.5': b'<?php $a="ab";$k=1.5;echo empty($a[$k]);',
 'isset-"ab"-NAN': b'<?php $a="ab";$k=NAN;echo isset($a[$k]);',
 'empty-"ab"-NAN': b'<?php $a="ab";$k=NAN;echo empty($a[$k]);',
 'isset-"ab"-"0x"': b'<?php $a="ab";$k="0x";echo isset($a[$k]);',
 'empty-"ab"-"0x"': b'<?php $a="ab";$k="0x";echo empty($a[$k]);',
 'isset-"ab"-" 0"': b'<?php $a="ab";$k=" 0";echo isset($a[$k]);',
 'empty-"ab"-" 0"': b'<?php $a="ab";$k=" 0";echo empty($a[$k]);',
 'isset-"ab"-[]': b'<?php $a="ab";$k=[];echo isset($a[$k]);',
 'empty-"ab"-[]': b'<?php $a="ab";$k=[];echo empty($a[$k]);',
 'isset-[]-null': b'<?php $a=[];$k=null;echo isset($a[$k]);',
 'empty-[]-null': b'<?php $a=[];$k=null;echo empty($a[$k]);',
 'isset-[]-false': b'<?php $a=[];$k=false;echo isset($a[$k]);',
 'empty-[]-false': b'<?php $a=[];$k=false;echo empty($a[$k]);',
 'isset-[]-true': b'<?php $a=[];$k=true;echo isset($a[$k]);',
 'empty-[]-true': b'<?php $a=[];$k=true;echo empty($a[$k]);',
 'isset-[]-0': b'<?php $a=[];$k=0;echo isset($a[$k]);',
 'empty-[]-0': b'<?php $a=[];$k=0;echo empty($a[$k]);',
 'isset-[]--1': b'<?php $a=[];$k=-1;echo isset($a[$k]);',
 'empty-[]--1': b'<?php $a=[];$k=-1;echo empty($a[$k]);',
 'isset-[]-99': b'<?php $a=[];$k=99;echo isset($a[$k]);',
 'empty-[]-99': b'<?php $a=[];$k=99;echo empty($a[$k]);',
 'isset-[]-1.5': b'<?php $a=[];$k=1.5;echo isset($a[$k]);',
 'empty-[]-1.5': b'<?php $a=[];$k=1.5;echo empty($a[$k]);',
 'isset-[]-NAN': b'<?php $a=[];$k=NAN;echo isset($a[$k]);',
 'empty-[]-NAN': b'<?php $a=[];$k=NAN;echo empty($a[$k]);',
 'isset-[]-"0x"': b'<?php $a=[];$k="0x";echo isset($a[$k]);',
 'empty-[]-"0x"': b'<?php $a=[];$k="0x";echo empty($a[$k]);',
 'isset-[]-" 0"': b'<?php $a=[];$k=" 0";echo isset($a[$k]);',
 'empty-[]-" 0"': b'<?php $a=[];$k=" 0";echo empty($a[$k]);',
 'isset-[]-[]': b'<?php $a=[];$k=[];echo isset($a[$k]);',
 'empty-[]-[]': b'<?php $a=[];$k=[];echo empty($a[$k]);',
 'compiler-descriptor-isset-globals': b'<?php isset($GLOBALS);',
 'compiler-descriptor-empty-globals': b'<?php empty($GLOBALS);',
 'compiler-descriptor-isset-two-globals': b'<?php isset($GLOBALS,$GLOBALS);',
 'compiler-descriptor-isset-variable': b'<?php isset($a);',
 'compiler-descriptor-isset-mixed': b'<?php isset($GLOBALS,$a);',
 'compiler-descriptor-empty-literal': b'<?php empty([]);',
 'compiler-descriptor-empty-list-effect': b'<?php empty((list($a)=[]));',
 'compiler-descriptor-empty-cast-list': b'<?php empty((bool)(list($a)=[]));',
 'compiler-descriptor-empty-coalesce-list': b'<?php empty((list($a)=[])??[1]);',
 'compiler-descriptor-empty-comparison-list': b'<?php empty((list($a)=[])===[]);',
 'compiler-descriptor-isset-globals-skip': b'<?php isset($GLOBALS)||[,$x];',
 'compiler-descriptor-isset-two-skip': b'<?php isset($GLOBALS,$GLOBALS)||[,$x];',
 'compiler-descriptor-isset-mixed-visit': b'<?php isset($GLOBALS,$a)||[,$x];',
 'compiler-descriptor-empty-list-skip': b'<?php empty((list($a)=[]))||[,$x];',
 'compiler-descriptor-empty-cast-visit': b'<?php empty((bool)(list($a)=[]))||[,$x];',
 'compiler-descriptor-empty-prepass-barrier': b'<?php [empty([[]=>1]),,];',
 'compiler-descriptor-second-argument-line': b'<?php isset($a,\n$b[\n]);',
 'compiler-descriptor-second-argument-name': b'<?php isset($a,\n${[1]});',
 'compiler-descriptor-nonvariable-priority': b'<?php isset([[]=>1]);',
 'author-multi-short-missing': b'<?php echo isset($missing,$also[$i++]);echo $i??"x";',
 'author-multi-short-null': b'<?php $a=null;echo isset($a,$also[$i++]);echo $i??"x";',
 'author-multi-all-present': b'<?php $a=1;$b=[2];echo isset($a,$b[0]);',
 'author-multi-later-null': b'<?php $a=1;$b=[null];echo isset($a,$b[0],$c[$i++]);echo $i??"x";',
 'author-multi-reference-name': b'<?php $a=1;$n="a";echo isset(${($r=&$n)},${($n="b")});echo $r;',
 'author-multi-reference-key': b'<?php $a=[1,2];$k=0;echo isset($a[($r=&$k)],$a[$k=1]);echo $r;',
 'author-multi-nested-effect': b'<?php $a=[1];$b=[2];echo isset($a[empty($missing)?0:1],$b[isset('
                               b'$a[0])?0:1]);',
 'author-empty-assign-cow': b'<?php $a=[1];echo empty($b=$a);$b[0]=2;echo $a[0],$b[0];',
 'author-empty-reference-assignment': b'<?php $a=0;echo empty($b=&$a);$b=3;echo $a;',
 'author-empty-list-effect': b'<?php echo empty(([$a]=[0]));echo $a;',
 'author-empty-throw': b'<?php echo empty(1/0);',
 'author-empty-nan-variable': b'<?php $a=NAN;echo empty($a);',
 'author-empty-nan-array': b'<?php $a=[NAN];echo empty($a[0]);',
 'author-isset-nan-array': b'<?php $a=[NAN];echo isset($a[0]);',
 'author-empty-nan-line': b'<?php $a=[NAN];\necho empty($a[\n0\n]);',
 'author-isset-float-line': b'<?php $a=[0=>1];$k=0.5;\necho isset($a[\n$k\n]);',
 'author-empty-float-line': b'<?php $a="0a";$k=0.5;\necho empty($a[\n$k\n]);',
 'author-isset-intermediate-array-key': b'<?php $a=[];echo isset($a[[]][0]);',
 'author-empty-intermediate-array-key': b'<?php $a=[];echo empty($a[[]][0]);',
 'author-isset-terminal-array-key': b'<?php $a=[];echo isset($a[0][[]]);',
 'author-empty-terminal-array-key': b'<?php $a=[];echo empty($a[0][[]]);',
 'author-isset-cv-base-rebind': b'<?php $a=[1];$b=[2];$n="a";echo isset($$n[($n="b")==="b"?0:1]);',
 'author-isset-temp-base-rebind': b'<?php $a=[1];$b=[2];$n="a";echo isset(${"".$n}[($n="b")==="b'
                                  b'"?0:1]);',
 'author-isset-temp-ref-base-rebind': b'<?php $a=[1];$b=[2];$n="a";echo isset(${($m=&$n)}[($n="b'
                                      b'")==="b"?0:1]);',
 'author-isset-array-temp-lifetime': b'<?php $a=[1];echo isset(($b=$a)[($a=[])?1:0]);echo $b[0];',
 'author-empty-array-temp-lifetime': b'<?php $a=[1];echo empty(($b=$a)[($a=[])?1:0]);echo $b[0];',
 'author-isset-foreach-reference-origin': b'<?php foreach([1,2] as &$v){$a=[$v];echo isset($a[$i'
                                          b'++]),empty($a[$i]);}echo $v;',
 'author-empty-foreach-result-alias': b'<?php $a=[1];foreach($a as &$v){echo empty($a[0]);}$v=2;'
                                      b'echo $a[0];',
 'author-isset-foreach-abrupt': b'<?php foreach([1] as &$v){$a=[];echo isset($a[[]]);}',
 'author-empty-loop-temporary': b'<?php $i=0;while($i++<3){echo empty(($a=[$i])[0]);}echo $a[0];',
 'author-isset-this-direct': b'<?php echo isset($this),empty($this);',
 'author-isset-this-intermediate': b'<?php echo isset($this[0]);',
 'author-empty-this-intermediate': b'<?php echo empty($this[0]);',
 'author-isset-this-computed': b'<?php $n="this";echo isset($$n),empty($$n);',
 'author-empty-constant-array-effects': b'<?php echo empty([($a=0),($b=1)]);echo $a,$b;',
 'author-isset-multiple-header': b'<?php echo isset($http_response_header,$a);echo $http_response_h'
                                 b'eader;',
 'string-index-extremes': b'<?php $s="0A";echo isset($s["9223372036854775808"]),empty($s["922337'
                          b'2036854775808"]),isset($s["-9223372036854775809"]),empty($s["-922337'
                          b'2036854775809"]);',
 'string-space-number': b'<?php $s="0A";echo isset($s[" 1"]),empty($s[" 0"]),isset($s["1e0"]),empt'
                        b'y($s["1.0"]);',
 'quiet-string-ancestor': b'<?php $a=["a0"];echo isset($a[0]["0x"][0]),empty($a[0]["1x"][0]);',
 'null-ancestor-effects': b'<?php $i=0;echo isset($a[++$i][++$i]),$i;echo empty($b[++$i][++$i]),'
                          b'$i;',
 'multi-isset-mutating-key': b'<?php $a=[1,2];$i=0;echo isset($a[$i],$a[++$i]),$i;',
 'nested-reference-key': b'<?php $a=[[3],[4]];$j=0;echo isset($a[($k=&$j)][($j=1)-1]),$k;',
 'nested-reference-key-absent': b'<?php $a=[[3]];$j=0;echo empty($a[($k=&$j)][($j=1)-1]),$k;',
 'multi-isset-abrupt-second': b'<?php $a=[1];echo isset($a[0],$a[[]],$missing);',
 'empty-ref-array-cow': b'<?php $x=[0];$r=&$x;$s=empty(($a=$r)[0]);$a[0]=9;echo $s,$x[0];',
 'empty-list-reference-result': b'<?php $v=1;echo empty(([&$a]=[&$v]));$a=3;echo $v;',
 'foreach-empty-origin': b'<?php foreach([0,1] as &$v){$a=[$v];echo empty($a[0]),isset($a[0]);}echo'
                         b' $v;',
 'empty-nan-selected-line': b'<?php $a=[NAN];echo empty(\n$a[0]\n);echo empty(\n(true ? NAN : 0)\n'
                            b');'}

PENDING_GLOBALS = {'isset-globals-temp': b'<?php echo isset(${true?"GLOBALS":"x"});',
 'empty-globals-temp': b'<?php echo empty(${true?"GLOBALS":"x"});',
 'isset-global-array-key': b'<?php echo isset($GLOBALS[[]]);',
 'empty-global-array-key': b'<?php echo empty($GLOBALS[[]]);'}

PREFIX = f.PREFIX

def main():
    paths=json.loads((D/'spec/semantics/modules.json').read_text());out=Path(tempfile.mkdtemp(prefix='isset-empty-state-',dir=ROOT/'.tools'))
    before=t.syntax_validation.implementation_fingerprint()
    manifest={p:hashlib.sha256((D/p).read_bytes()).hexdigest() for p in paths}
    selection=['author-multi-short-missing', 'author-multi-reference-key', 'author-empty-assign-cow', 'author-empty-reference-assignment', 'author-isset-temp-ref-base-rebind', 'author-empty-foreach-result-alias', 'author-isset-foreach-abrupt', 'author-empty-constant-array-effects', 'author-empty-nan-line']
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
    assert before==t.syntax_validation.implementation_fingerprint(),'isset/empty gate inputs changed'
    report={'fingerprint':before,'result':'pass' if all(x['run']['status']==0 and x['run']['stdout'].strip()=='true' for x in records) else 'fail','inputs':manifest,'records':records,'assertions':sum(x['assertions'] for x in records)};(out/'results.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'coverage/semantics/isset-empty.json').write_text(json.dumps(report,indent=2)+'\n');assert report['result']=='pass',str(out);print(out,report['result'],report['assertions'])

if __name__=='__main__':main()
