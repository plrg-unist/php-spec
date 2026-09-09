#!/usr/bin/env python3
"""Increment/decrement value snapshots, RW acquisition, diagnostics and resumption."""
import base64, json, re, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/semantics'))
import static_types as types

NORMAL_CASES = {
    '++$a-1': b'<?php $a=1;echo ++$a;echo ":",$a;',
    '++$a-null': b'<?php $a=null;echo ++$a;echo ":",$a;',
    '++$a-true': b'<?php $a=true;echo ++$a;echo ":",$a;',
    '++$a-false': b'<?php $a=false;echo ++$a;echo ":",$a;',
    '++$a-""': b'<?php $a="";echo ++$a;echo ":",$a;',
    '++$a-"ZZ"': b'<?php $a="ZZ";echo ++$a;echo ":",$a;',
    '++$a-"1e2"': b'<?php $a="1e2";echo ++$a;echo ":",$a;',
    '++$a-PHP_INT_MAX': b'<?php $a=PHP_INT_MAX;echo ++$a;echo ":",$a;',
    '++$a-PHP_INT_MIN': b'<?php $a=PHP_INT_MIN;echo ++$a;echo ":",$a;',
    '++$a-NAN': b'<?php $a=NAN;echo ++$a;echo ":",$a;',
    '++$a-INF': b'<?php $a=INF;echo ++$a;echo ":",$a;',
    '$a++-1': b'<?php $a=1;echo $a++;echo ":",$a;',
    '$a++-null': b'<?php $a=null;echo $a++;echo ":",$a;',
    '$a++-true': b'<?php $a=true;echo $a++;echo ":",$a;',
    '$a++-false': b'<?php $a=false;echo $a++;echo ":",$a;',
    '$a++-""': b'<?php $a="";echo $a++;echo ":",$a;',
    '$a++-"ZZ"': b'<?php $a="ZZ";echo $a++;echo ":",$a;',
    '$a++-"1e2"': b'<?php $a="1e2";echo $a++;echo ":",$a;',
    '$a++-PHP_INT_MAX': b'<?php $a=PHP_INT_MAX;echo $a++;echo ":",$a;',
    '$a++-PHP_INT_MIN': b'<?php $a=PHP_INT_MIN;echo $a++;echo ":",$a;',
    '$a++-NAN': b'<?php $a=NAN;echo $a++;echo ":",$a;',
    '$a++-INF': b'<?php $a=INF;echo $a++;echo ":",$a;',
    '--$a-1': b'<?php $a=1;echo --$a;echo ":",$a;',
    '--$a-null': b'<?php $a=null;echo --$a;echo ":",$a;',
    '--$a-true': b'<?php $a=true;echo --$a;echo ":",$a;',
    '--$a-false': b'<?php $a=false;echo --$a;echo ":",$a;',
    '--$a-""': b'<?php $a="";echo --$a;echo ":",$a;',
    '--$a-"ZZ"': b'<?php $a="ZZ";echo --$a;echo ":",$a;',
    '--$a-"1e2"': b'<?php $a="1e2";echo --$a;echo ":",$a;',
    '--$a-PHP_INT_MAX': b'<?php $a=PHP_INT_MAX;echo --$a;echo ":",$a;',
    '--$a-PHP_INT_MIN': b'<?php $a=PHP_INT_MIN;echo --$a;echo ":",$a;',
    '--$a-NAN': b'<?php $a=NAN;echo --$a;echo ":",$a;',
    '--$a-INF': b'<?php $a=INF;echo --$a;echo ":",$a;',
    '$a---1': b'<?php $a=1;echo $a--;echo ":",$a;',
    '$a---null': b'<?php $a=null;echo $a--;echo ":",$a;',
    '$a---true': b'<?php $a=true;echo $a--;echo ":",$a;',
    '$a---false': b'<?php $a=false;echo $a--;echo ":",$a;',
    '$a---""': b'<?php $a="";echo $a--;echo ":",$a;',
    '$a---"ZZ"': b'<?php $a="ZZ";echo $a--;echo ":",$a;',
    '$a---"1e2"': b'<?php $a="1e2";echo $a--;echo ":",$a;',
    '$a---PHP_INT_MAX': b'<?php $a=PHP_INT_MAX;echo $a--;echo ":",$a;',
    '$a---PHP_INT_MIN': b'<?php $a=PHP_INT_MIN;echo $a--;echo ":",$a;',
    '$a---NAN': b'<?php $a=NAN;echo $a--;echo ":",$a;',
    '$a---INF': b'<?php $a=INF;echo $a--;echo ":",$a;',
    'location-0': b'<?php echo ++$a;echo $a;',
    'location-1': b'<?php echo --$a;echo $a;',
    'location-2': b'<?php $a=[];echo ++$a[0];echo $a[0];',
    'location-3': b'<?php echo ++$a[0][0];echo $a[0][0];',
    'location-4': b'<?php echo ++$a[][0];echo $a[0][0];',
    'location-5': b'<?php $a=false;$r=&$a;echo ++$a[0];echo $r[0];',
    'location-6': b'<?php $x=1;$a=[&$x];echo $a[0]++;echo $x;',
    'location-7': b'<?php $a=[1];$b=$a;echo ++$b[0];echo $a[0],$b[0];',
    'location-8': b'<?php $a=1;$n="a";echo ++$$n;echo $a;',
    'timing-0': b'<?php $a=1;echo ($a++)===1,($a)===2,(++$a)===3;',
    'timing-1': b'<?php $a=1;echo $a+++$a;echo ++$a+$a;',
    'timing-2': b'<?php $a=1;$r=&$a;echo $r+++($a=5);echo $r;',
    'timing-3': b'<?php $a=[1];echo ++$a[($a=[5])[0]-5];echo $a[0];',
    'timing-4': b'<?php $a=[1];$b=[9];echo $a[($a=&$b)[0]-9]++;echo $a[0],$b[0];',
    'timing-5': b'<?php $a=[1];$b=$a;echo $a[0]+++($a[0]=9);echo $b[0],$a[0];',
    'timing-6': b'<?php $x="a";$a=1;echo ++${($n=&$x)};echo $a,$n;',
    'timing-7': b'<?php\n++\n$a[\n$key\n];echo $a[null];',
    'timing-8': b'<?php\n$a="";echo\n--\n$a;',
    'result-type-0': b'<?php $a=PHP_INT_MAX;$r=$a++;echo $r===PHP_INT_MAX,$a===(PHP_INT_MAX+1);',
    'result-type-1': b'<?php $a=PHP_INT_MIN;$r=$a--;echo $r===PHP_INT_MIN,$a===(PHP_INT_MIN-1);',
    'result-type-2': b'<?php $a=null;$r=$a++;echo $r===null,$a===1;',
    'result-type-3': b'<?php $a=null;$r=$a--;echo $r===null,$a===null;',
    'result-type-4': b'<?php $a=true;$r=$a++;echo $r===true,$a===true;',
    'result-type-5': b'<?php $a=false;$r=--$a;echo $r===false,$a===false;',
    'result-type-6': b'<?php $a="9";$r=++$a;echo $r===10,$a===10;',
    'result-type-7': b'<?php $a="1.5";$r=$a++;echo $r==="1.5",$a===2.5;',
    'result-type-8': b'<?php $a="";$r=$a++;echo $r==="",$a==="1";',
    'result-type-9': b'<?php $a="";$r=$a--;echo $r==="",$a===-1;',
    'result-type-10': b'<?php $a="ZZ";$r=++$a;echo $r==="AAA",$a==="AAA";',
    'loop-update': b'<?php $a=false;$r=&$a;for($i=0;$i<3;$i++){$a=false;echo ++$a[0];echo $r[0];}',
    'loop-copy': b'<?php $a=[1];$i=0;while($i++<3){$b=$a;echo $b[0]++;echo $a[0],$b[0];}',
    'error-0': b'<?php $a=[];echo ++$a;',
    'error-1': b'<?php $a=[];echo $a--;',
    'error-2': b'<?php $a="abc";echo ++$a[0];',
    'error-3': b'<?php $a="abc";echo $a["x"]++;',
    'error-4': b'<?php $a="abc";echo $a[1.5]--;',
    'error-5': b'<?php $a="abc";echo --$a[[]];',
    'error-6': b'<?php $a="abc";echo ++$a[];',
    'error-7': b'<?php $a="abc";echo ++$a[0][0];',
    'error-8': b'<?php $a=1;echo ++$a[0];',
    'error-9': b'<?php $a=true;echo --$a[0];',
    'error-10': b'<?php $a=[];echo ++$a[[]];',
    'error-11': b'<?php $a=[PHP_INT_MAX=>1];echo ++$a[];',
    'error-12': b'<?php $a="abc";echo ++$a[$missing];',
    'prepass-0': b'<?php $a=1;$b=[$a++];echo $b[0],$a;',
    'prepass-1': b'<?php $a=1;$b=[$a++=>9];echo $b[1],$a;',
    'prepass-2': b'<?php $a=1;echo [true ? 7 : $a++][0],$a;',
    'prepass-3': b'<?php $a=2;$b=[++$a];echo $b[0],$a;',
    'prepass-4': b'<?php $a=2;$b=[--$a];echo $b[0],$a;',
    'prepass-5': b'<?php $a=2;$b=[$a--];echo $b[0],$a;',
    'prepass-6': b'<?php $a=2;$b=[++$a=>9];echo $b===[3=>9],$a;',
    'prepass-7': b'<?php $a=2;$b=[--$a=>9];echo $b===[1=>9],$a;',
    'prepass-8': b'<?php $a=2;$b=[$a--=>9];echo $b===[2=>9],$a;',
    'prepass-9': b'<?php $a=1;echo [$a++][0],$a;',
    'prepass-10': b'<?php $a=0;$b=[$a++ || ++$a];echo $b[0],$a;',
    'prepass-11': b'<?php $a=false;$b=[&$a,$a[0]++];echo $b[1]===null,$a[0];',
    'prepass-12': b'<?php $a=[];$b=[++$a[0]=>&$a[0]];echo $b[1],$a[0];',
    'prepass-13': b'<?php $b=[false && ++$a["bad"]];echo $b[0]===false;',
    'prepass-14': b'<?php echo [false && ++$a[[[]=>1]]][0];',
    'global-this-0': b'<?php $this++;',
    'global-this-1': b'<?php ++$this;',
    'global-this-2': b'<?php $this--;',
    'global-this-3': b'<?php --$this;',
    'global-this-4': b'<?php echo $this;',
    'global-this-5': b'<?php echo ${"this"};',
    'global-this-6': b'<?php ++${"this"};',
    'global-this-7': b'<?php $n="this";echo $$n;',
    'global-this-8': b'<?php $n="this";++$$n;',
    'global-this-9': b'<?php $n="this";$$n++;',
    'global-this-10': b'<?php $n="this";--$$n;',
    'global-this-11': b'<?php $n="this";$$n--;',
    'global-this-12': b'<?php false && ++$this;echo 1;',
    'global-this-13': b'<?php echo [true?1:$this++][0];',
    'global-this-14': b'<?php echo [false && ++$this[[[]=>1]]][0];',
    'global-this-15': b'<?php echo $this+(0+$missing);',
    'global-this-16': b'<?php ++$this[(0+$missing)];',
    'global-this-17': b'<?php $this[(0+$missing)]=1;',
    'global-this-18': b'<?php $a=&$this[(0+$missing)];',
    'global-this-19': b'<?php unset($this[(0+$missing)]);',
    'global-this-20': b'<?php echo $this[(0+$missing)];',
    'global-this-21': b'<?php $n="this";echo $$n+(0+$missing);',
    'global-this-22': b'<?php $n="this";++$$n[(0+$missing)];',
    'global-this-23': b'<?php $n="this";$$n[($missing+1)]++;',
    'global-this-24': b'<?php $n="this";$$n[$missing]++;',
    'global-this-25': b'<?php $x=&$this;',
    'global-this-26': b'<?php $a=[&$this];',
    'global-this-27': b'<?php $a[$missing+1]=&$this;',
    'global-this-28': b'<?php $n="this";echo $$n[(0+$missing)];',
    'global-this-29': b'<?php echo ${(true?"this":"a")};',
    'global-this-30': b'<?php ++${(true?"this":"a")};',
    'global-this-31': b'<?php ${(true?"this":"a")}++;',
    'global-this-32': b'<?php --${(true?"this":"a")};',
    'global-this-33': b'<?php ${(true?"this":"a")}--;',
    'global-this-34': b'<?php ++${(true?"this":"a")}[(0+$missing)];',
    'global-this-35': b'<?php $n="a";$$n=false;$a[0][0]=1;echo $a[0][0];',
    'global-this-36': b'<?php $a=false;$r=&$a;unset($r);$n="a";$$n=false;$a[0][0]=1;echo $a[0][0];',
    'review-incdec-computed-line-originals-0': b'<?php\n$n="this";\necho ++${(true?"this":"a")}[\n$missing\n];',
    'review-incdec-computed-line-originals-1': b'<?php\n$n="this";\necho ++$$n[\n$missing\n];',
    'review-incdec-computed-line-originals-2': b'<?php\n$n="this";\necho ++$$n[\n(0+$missing)\n];',
    'review-incdec-computed-line-originals-3': b'<?php\n$n="a";\necho ++$$n[\n0\n];',
    'review-incdec-computed-line-originals-4': b'<?php\necho ++$a[\n0\n];',
    'review-incdec-computed-line-originals-5': b'<?php\necho ++$this[\n$missing\n];',
    'review-incdec-computed-line-originals-6': b'<?php\n$n="a";\necho $$n[\n0\n];',
    'review-review5-this-originals-5': b'<?php ${"this"}++;',
    'review-review5-this-originals-6': b'<?php $this[$missing]++;',
    'review-review5-this-originals-7': b'<?php $this[($missing+1)]++;',
    'review-review5-this-originals-9': b'<?php false&&$this++;echo 1;',
    'review-review5-this-originals-11': b'<?php $this\n[\n$missing\n]++;',
    'review-this-context-originals-8': b'<?php $this[0]++;',
    'review-this-context-originals-9': b'<?php $n="this";$$n[0]++;',
}

CASES = {"incdec-"+name: source for name,source in NORMAL_CASES.items()}


# Exact source bytes from the dedicated compiler phase and emission gates.
CASES.update({
    'incdec-phase-pre++$x': b'<?php use A; ++$x; use B;',
    'incdec-phase-pre++$a[]': b'<?php use A; ++$a[]; use B;',
    'incdec-phase-pre++$a[0][]': b'<?php use A; ++$a[0][]; use B;',
    'incdec-phase-pre++${"name"}': b'<?php use A; ++${"name"}; use B;',
    'incdec-phase-pre++$a[NAN == true]': b'<?php use A; ++$a[NAN == true]; use B;',
    'incdec-phase-post++$x': b'<?php use A; $x++; use B;',
    'incdec-phase-post++$a[]': b'<?php use A; $a[]++; use B;',
    'incdec-phase-post++$a[0][]': b'<?php use A; $a[0][]++; use B;',
    'incdec-phase-post++${"name"}': b'<?php use A; ${"name"}++; use B;',
    'incdec-phase-post++$a[NAN == true]': b'<?php use A; $a[NAN == true]++; use B;',
    'incdec-phase-pre--$x': b'<?php use A; --$x; use B;',
    'incdec-phase-pre--$a[]': b'<?php use A; --$a[]; use B;',
    'incdec-phase-pre--$a[0][]': b'<?php use A; --$a[0][]; use B;',
    'incdec-phase-pre--${"name"}': b'<?php use A; --${"name"}; use B;',
    'incdec-phase-pre--$a[NAN == true]': b'<?php use A; --$a[NAN == true]; use B;',
    'incdec-phase-post--$x': b'<?php use A; $x--; use B;',
    'incdec-phase-post--$a[]': b'<?php use A; $a[]--; use B;',
    'incdec-phase-post--$a[0][]': b'<?php use A; $a[0][]--; use B;',
    'incdec-phase-post--${"name"}': b'<?php use A; ${"name"}--; use B;',
    'incdec-phase-post--$a[NAN == true]': b'<?php use A; $a[NAN == true]--; use B;',
    'incdec-phase-inc-after-failure': b'<?php [&$x[]]; ++$a[NAN == true];',
    'incdec-phase-inc-before-failure': b'<?php ++$a[NAN == true]; [&$x[]];',
    'incdec-phase-inc-nested-failure': b'<?php ++$a[[&$x[]]];',
    'incdec-phase-inc-lines': b'<?php ++\n$a[\nNAN == true\n];',
    'incdec-phase-inc-name-lines': b'<?php ++\n${\n"x"\n};',
    'incdec-phase-header-rw': b'<?php $http_response_header++;',
    'incdec-phase-header-write': b'<?php $http_response_header=1;',
    'incdec-phase-this-rw': b'<?php $this++;',
    'incdec-phase-globals-rw': b'<?php $GLOBALS++;',
    'incdec-phase-function-rw': b'<?php foo()++;',
    'incdec-phase-method-rw': b'<?php $x->foo()++;',
    'incdec-phase-string-offset': b'<?php $x="1"; $x[0]++;',
    'incdec-phase-reject-target-0': b'<?php\nfoo([&$q[]])++;',
    'incdec-phase-reject-target-1': b'<?php\n$x->foo([&$q[]])++;',
    'incdec-phase-reject-target-2': b'<?php\n$x?->foo([&$q[]])++;',
    'incdec-phase-reject-target-3': b'<?php\nA::foo([&$q[]])++;',
    'incdec-phase-reject-target-4': b'<?php\n$x?->p++;',
    'incdec-phase-reject-target-5': b'<?php\n$x?->p[0]++;',
    'incdec-phase-reject-target-6': b'<?php\n$x?->p->q++;',
    'incdec-phase-reject-target-7': b'<?php\n(\n$f\n)()++;',
    'incdec-phase-reject-target-8': b'<?php\n(\n$x\n)->foo()++;',
    'incdec-phase-array-value-++$a': b'<?php $a=1;$b=[++$a];',
    'incdec-phase-array-key-++$a': b'<?php $a=1;$b=[++$a=>1];',
    'incdec-phase-logical-skipped-++$a': b'<?php $a=1;false && [++$a];',
    'incdec-phase-ternary-skipped-++$a': b'<?php $a=1;$b=[true?1:++$a];',
    'incdec-phase-ordinary-visited-++$a': b'<?php $a=1;$b=[false?1:++$a];',
    'incdec-phase-array-value-$a++': b'<?php $a=1;$b=[$a++];',
    'incdec-phase-array-key-$a++': b'<?php $a=1;$b=[$a++=>1];',
    'incdec-phase-logical-skipped-$a++': b'<?php $a=1;false && [$a++];',
    'incdec-phase-ternary-skipped-$a++': b'<?php $a=1;$b=[true?1:$a++];',
    'incdec-phase-ordinary-visited-$a++': b'<?php $a=1;$b=[false?1:$a++];',
    'incdec-phase-array-value---$a': b'<?php $a=1;$b=[--$a];',
    'incdec-phase-array-key---$a': b'<?php $a=1;$b=[--$a=>1];',
    'incdec-phase-logical-skipped---$a': b'<?php $a=1;false && [--$a];',
    'incdec-phase-ternary-skipped---$a': b'<?php $a=1;$b=[true?1:--$a];',
    'incdec-phase-ordinary-visited---$a': b'<?php $a=1;$b=[false?1:--$a];',
    'incdec-phase-array-value-$a--': b'<?php $a=1;$b=[$a--];',
    'incdec-phase-array-key-$a--': b'<?php $a=1;$b=[$a--=>1];',
    'incdec-phase-logical-skipped-$a--': b'<?php $a=1;false && [$a--];',
    'incdec-phase-ternary-skipped-$a--': b'<?php $a=1;$b=[true?1:$a--];',
    'incdec-phase-ordinary-visited-$a--': b'<?php $a=1;$b=[false?1:$a--];',
    'incdec-phase-prepass-order-0': b'<?php use A;$b=[++$a[[&$q[]]]];use B;',
    'incdec-phase-prepass-order-1': b'<?php use A;$b=[foo([&$q[]])++];use B;',
    'incdec-phase-prepass-order-2': b'<?php use A;$b=[true?1:foo([&$q[]])++];use B;',
    'incdec-phase-prepass-order-3': b'<?php use A;$b=[false && foo([&$q[]])++];use B;',
    'incdec-phase-prepass-order-4': b'<?php use A;$b=[++$a[NAN == true], [&$q[]]];use B;',
    'incdec-phase-prepass-order-5': b'<?php use A;$b=[++$a[[&$q[]]], NAN == true];use B;',
    'incdec-phase-deep-barrier-skipped': b'<?php echo [false && ++$a[[[]=>1]]][0];',
    'incdec-phase-deep-barrier-visited': b'<?php echo [true && ++$a[[[]=>1]]][0];',
    'incdec-phase-retained-array-value': b'<?php $a=1;$b=[$a++];echo $b[0],$a;',
    'incdec-phase-retained-array-key': b'<?php $a=1;$b=[$a++=>9];echo $b[1],$a;',
    'incdec-phase-retained-skipped-control': b'<?php $a=1;echo [true ? 7 : $a++][0],$a;',
    'incdec-phase-callable-line-0': b'<?php\n(\n$f\n)()++;',
    'incdec-phase-callable-line-1': b'<?php\n(\n$f)\n()++;',
    'incdec-phase-callable-line-2': b'<?php\n$f\n(\n[&$q[]]\n)++;',
    'incdec-phase-callable-line-3': b'<?php\nfoo\n(\n[&$q[]]\n)++;',
    'incdec-phase-callable-line-4': b'<?php\n$f\n(\n1\n)++;',
    'incdec-phase-callable-line-5': b'<?php\n$f(\n\n1\n)++;',
    'incdec-phase-callable-line-6': b'<?php\n$f\n( \n1\n)++;',
    'incdec-phase-callable-line-7': b'<?php\n$f (\n\n1\n)++;',
    'incdec-phase-this-literal-0': b'<?php use A;$this=1;use B;',
    'incdec-phase-this-literal-1': b'<?php use A;$this=&$x;use B;',
    'incdec-phase-this-literal-2': b'<?php use A;unset($this);use B;',
    'incdec-phase-this-literal-3': b'<?php use A;$a=&$this;use B;',
    'incdec-phase-this-literal-4': b'<?php use A;$this[0]=1;use B;',
    'incdec-phase-this-literal-5': b'<?php use A;unset($this[0]);use B;',
    'incdec-phase-this-literal-6': b'<?php use A;$this=[&$a[]];use B;',
    'incdec-phase-this-literal-7': b'<?php use A;$this=&$a[];use B;',
    'incdec-phase-this-literal-8': b'<?php use A;false && ($this=1);use B;',
    'incdec-phase-this-literal-9': b'<?php use A;[true?1:($this=1)];use B;',
    'incdec-phase-this-literal-10': b'<?php use A;[false && ($this=1)];use B;',
    'incdec-phase-this-literal-11': b'<?php use A;unset($x[],$this);use B;',
    'incdec-phase-this-literal-12': b'<?php use A;unset($x[\n0\n],\n$this);use B;',
    'incdec-phase-this-literal-13': b'<?php use A;\n$this\n=\n1;use B;',
    'incdec-phase-this-string-0': b'<?php use A;${"this"}=1;use B;',
    'incdec-phase-this-string-1': b'<?php use A;${"this"}=&$x;use B;',
    'incdec-phase-this-string-2': b'<?php use A;unset(${"this"});use B;',
    'incdec-phase-this-string-3': b'<?php use A;$a=&${"this"};use B;',
    'incdec-phase-this-string-4': b'<?php use A;${"this"}[0]=1;use B;',
    'incdec-phase-this-string-5': b'<?php use A;unset(${"this"}[0]);use B;',
    'incdec-phase-this-string-6': b'<?php use A;${"this"}=[&$a[]];use B;',
    'incdec-phase-this-string-7': b'<?php use A;${"this"}=&$a[];use B;',
    'incdec-phase-this-string-8': b'<?php use A;false && (${"this"}=1);use B;',
    'incdec-phase-this-string-9': b'<?php use A;[true?1:(${"this"}=1)];use B;',
    'incdec-phase-this-string-10': b'<?php use A;[false && (${"this"}=1)];use B;',
    'incdec-phase-this-string-11': b'<?php use A;unset($x[],${"this"});use B;',
    'incdec-phase-this-string-12': b'<?php use A;unset($x[\n0\n],\n${"this"});use B;',
    'incdec-phase-this-string-13': b'<?php use A;\n${"this"}\n=\n1;use B;',
    'incdec-phase-line-0': b'<?php $a=true;\necho ++\n$a;',
    'incdec-phase-line-1': b'<?php $a=true;\necho --\n$a;',
    'incdec-phase-line-2': b'<?php $a=true;\necho $a\n++;',
    'incdec-phase-line-3': b'<?php $a=true;\necho $a\n--;',
    'incdec-phase-line-4': b'<?php $a=[];\necho ++$a[\n0\n];',
    'incdec-phase-line-5': b'<?php $a=[];\necho --$a[\n0\n];',
    'incdec-phase-line-6': b'<?php $a=[];\necho $a[\n0\n]++;',
    'incdec-phase-line-7': b'<?php $a=[];\necho $a[\n0\n]--;',
    'incdec-prepass-depth-visited': b'<?php echo [true && ++$a[[[]=>1]]][0];',
})

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
            source_path=Path(tmp)/'incdec.php'
            for name,source in NORMAL_CASES.items():
                source_path.write_bytes(source)
                native=subprocess.run([str(types.PHP),'-n',*types.FLAGS,str(source_path)],capture_output=True,env=types.ENV,timeout=10)
                assert native.returncode in (0,255),(name,native.stdout,native.stderr)
                completion='NORMAL'
                if native.returncode==255:
                    match=re.search(rb'Uncaught (Error|TypeError): (.*?) in '+re.escape(str(source_path).encode())+rb':(\d+)',native.stderr);assert match,native.stderr
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
                    for budget in (1,2,5,9,17,31,63):
                        checks += [f'S_budget{budget} = $drive(S, {budget})',
                                   f'$drive(S_budget{budget}[.COMPLETION = NORMAL], 10000) = S_out',
                                   f'S_budget{budget}.POOLS = S.POOLS',
                                   f'S_budget{budget}.CODE = S.CODE',
                                   f'$heap_valid($heap_graph(S_budget{budget}))']
                assertions.append(checks)
                records.append({'id':name,'source_base64':base64.b64encode(source).decode(),'ast':checked['ast'],
                                'oracle_exit_status':native.returncode,'oracle_stdout':base64.b64encode(native.stdout).decode(),
                                'oracle_stderr':base64.b64encode(native.stderr).decode()})
            for index,checks in enumerate(assertions):
                fixture=Path(tmp)/'incdec.watsup'
                fixture.write_text(PREFIX+'dec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+check+'\n' for check in checks))
                run=subprocess.run([str(runner),*map(str,specs),str(fixture)],capture_output=True,text=True,cwd=ROOT,timeout=120)
                if run.returncode or run.stdout.strip()!='true':
                    (ROOT/'.tools/incdec-this-line-source-failure.watsup').write_text(fixture.read_text())
                    raise AssertionError((index,run.stdout,run.stderr))
    finally:
        frontend.close();adapter.close()
    assert before==types.syntax_validation.implementation_fingerprint(),'inputs changed during wrapper gate'
    report={'result':'pass','classification':'checked-source increment/decrement values, RW locations, global this context, diagnostics and budget resumption; currently admitted scalar and array forms',
            'source_cases':len(records),'state_cases':len(assertions),'assertions':sum(map(len,assertions)),
            'records':records,'fingerprint':before}
    (ROOT/'coverage/semantics/incdec.json').write_text(json.dumps(report,indent=2)+'\n')
    print({key:report[key] for key in ('result','source_cases','state_cases','assertions')})

if __name__=='__main__':
    main()
