#!/usr/bin/env python3
"""Coalescing assignment compile phases, distinct read/write lines and memoization."""
import base64,hashlib,json,subprocess,tempfile
from pathlib import Path
import source_compiler as compiler
from source_compiler import types,context
ROOT=Path(__file__).resolve().parents[2]
REPORT=ROOT/'coverage/semantics/coalesce-assignment-compiler.json'

SOURCES = [('name/empty-array/read', b'<?php echo "A";echo ${\n[]\n};echo "B";'),
 ('name/empty-array/write', b'<?php echo "A";${\n[]\n}=7;echo "B";'),
 ('name/empty-array/unset', b'<?php echo "A";unset(${\n[]\n});echo "B";'),
 ('name/empty-array/quiet', b'<?php echo "A";echo ${\n[]\n}??7;echo "B";'),
 ('name/empty-array/coalesce-write', b'<?php echo "A";${\n[]\n}??=7;echo "B";'),
 ('name/empty-array/reference', b'<?php echo "A";$r=&${\n[]\n};echo "B";'),
 ('name/array/read', b'<?php echo "A";echo ${\n[1]\n};echo "B";'),
 ('name/array/write', b'<?php echo "A";${\n[1]\n}=7;echo "B";'),
 ('name/array/unset', b'<?php echo "A";unset(${\n[1]\n});echo "B";'),
 ('name/array/quiet', b'<?php echo "A";echo ${\n[1]\n}??7;echo "B";'),
 ('name/array/coalesce-write', b'<?php echo "A";${\n[1]\n}??=7;echo "B";'),
 ('name/array/reference', b'<?php echo "A";$r=&${\n[1]\n};echo "B";'),
 ('name/nan/read', b'<?php echo "A";echo ${\nNAN\n};echo "B";'),
 ('name/nan/write', b'<?php echo "A";${\nNAN\n}=7;echo "B";'),
 ('name/nan/unset', b'<?php echo "A";unset(${\nNAN\n});echo "B";'),
 ('name/nan/quiet', b'<?php echo "A";echo ${\nNAN\n}??7;echo "B";'),
 ('name/nan/coalesce-write', b'<?php echo "A";${\nNAN\n}??=7;echo "B";'),
 ('name/nan/reference', b'<?php echo "A";$r=&${\nNAN\n};echo "B";'),
 ('name/infinity/read', b'<?php echo "A";echo ${\nINF\n};echo "B";'),
 ('name/infinity/write', b'<?php echo "A";${\nINF\n}=7;echo "B";'),
 ('name/infinity/unset', b'<?php echo "A";unset(${\nINF\n});echo "B";'),
 ('name/infinity/quiet', b'<?php echo "A";echo ${\nINF\n}??7;echo "B";'),
 ('name/infinity/coalesce-write', b'<?php echo "A";${\nINF\n}??=7;echo "B";'),
 ('name/infinity/reference', b'<?php echo "A";$r=&${\nINF\n};echo "B";'),
 ('name/list-effect/read', b'<?php echo "A";echo ${\n(list($x)=[1])\n};echo "B";'),
 ('name/list-effect/write', b'<?php echo "A";${\n(list($x)=[1])\n}=7;echo "B";'),
 ('name/list-effect/unset', b'<?php echo "A";unset(${\n(list($x)=[1])\n});echo "B";'),
 ('name/list-effect/quiet', b'<?php echo "A";echo ${\n(list($x)=[1])\n}??7;echo "B";'),
 ('name/list-effect/coalesce-write', b'<?php echo "A";${\n(list($x)=[1])\n}??=7;echo "B";'),
 ('name/list-effect/reference', b'<?php echo "A";$r=&${\n(list($x)=[1])\n};echo "B";'),
 ('name/list-nested-effect/read', b'<?php echo "A";echo ${\n(list($x)=[[1]])\n};echo "B";'),
 ('name/list-nested-effect/write', b'<?php echo "A";${\n(list($x)=[[1]])\n}=7;echo "B";'),
 ('name/list-nested-effect/unset', b'<?php echo "A";unset(${\n(list($x)=[[1]])\n});echo "B";'),
 ('name/list-nested-effect/quiet', b'<?php echo "A";echo ${\n(list($x)=[[1]])\n}??7;echo "B";'),
 ('name/list-nested-effect/coalesce-write', b'<?php echo "A";${\n(list($x)=[[1]])\n}??=7;echo "B";'),
 ('name/list-nested-effect/reference', b'<?php echo "A";$r=&${\n(list($x)=[[1]])\n};echo "B";'),
 ('line/float-key-constant', b'<?php $a=[];\n$a[1.2+\n0] ??=\n7;'),
 ('line/float-key-temp', b'<?php $a=[];$k=1.2;\n$a[$k+\n0] ??=\n7;'),
 ('line/float-key-cv', b'<?php $a=[];$k=1.2;\n$a[\n$k] ??=\n7;'),
 ('line/float-key-nullbase', b'<?php $a=null;\n$a[1.2+\n0] ??=\n7;'),
 ('line/float-key-falsebase', b'<?php $a=false;\n$a[1.2+\n0] ??=\n7;'),
 ('line/float-key-truebase', b'<?php $a=true;\n$a[1.2+\n0] ??=\n7;'),
 ('line/float-key-selected', b'<?php $a=[1=>8];\n$a[1.2+\n0] ??=\n7;'),
 ('line/float-key-throwrhs', b'<?php $a=[];\n$a[1.2+\n0] ??=\n1/0;'),
 ('line/nested-falsebase', b'<?php $a=false;\n$a[1.2+\n0][2.3+\n0] ??=\n7;'),
 ('line/nested-truebase', b'<?php $a=true;\n$a[1.2+\n0][2.3+\n0] ??=\n7;'),
 ('line/nested-arraybase', b'<?php $a=[];\n$a[1.2+\n0][2.3+\n0] ??=\n7;'),
 ('line/key-array-early', b'<?php $a=[];\n$a[[]] ??=\n1/0;'),
 ('line/name-this-cv', b'<?php $n="this";\n${\n$n} ??=\n7;'),
 ('line/name-this-temp', b'<?php $n="this";\n${"".\n$n} ??=\n7;'),
 ('line/name-this-cast', b'<?php $n="this";\n${(string)\n$n} ??=\n7;'),
 ('line/name-globals-temp', b'<?php $n="GLOBALS";\n${"".\n$n} ??=\n7;'),
 ('line/key-undefined-cv', b'<?php $a=[];\n$a[\n$k] ??=\n7;'),
 ('line/key-undefined-temp', b'<?php $a=[];\n$a[$k+\n0] ??=\n7;'),
 ('line/name-undefined-cv', b'<?php ${\n$n} ??=\n7;'),
 ('line/name-undefined-temp', b'<?php ${"".\n$n} ??=\n7;'),
 ('target/this', b'<?php $this ??= [,$x];'),
 ('target/this-concat', b'<?php ${"th"."is"} ??= [,$x];'),
 ('target/this-temp', b'<?php ${true?"this":"x"} ??= [,$x];'),
 ('target/globals', b'<?php $GLOBALS ??= [,$x];'),
 ('target/globals-temp', b'<?php ${true?"GLOBALS":"x"} ??= [,$x];'),
 ('target/function', b'<?php foo() ??= [,$x];'),
 ('target/method', b'<?php $x->foo() ??= [,$x];'),
 ('target/staticmethod', b'<?php C::foo() ??= [,$x];'),
 ('target/nullsafemethod', b'<?php $x?->foo() ??= [,$x];'),
 ('target/nullsafeprop', b'<?php $x?->p ??= [,$x];'),
 ('target/nullsafepropdim', b'<?php $x?->p[0] ??= [,$x];'),
 ('target/append', b'<?php $x[] ??= [,$x];'),
 ('target/temporary-dim', b'<?php [1][0] ??= 7;'),
 ('target/temporary-dim-hole-right', b'<?php [1][0] ??= [,$x];'),
 ('target/header-self', b'<?php $http_response_header ??= $http_response_header;echo $http_response_header;'),
 ('target/header-dim-rhs', b'<?php $a[\n$k] ??=\n$http_response_header;echo $http_response_header;'),
 ('reference/key-reference-rhs-mutates',
  b'<?php $a=[];$j=1;$a[($k=&$j)]??=($j=2);echo $a[1]??"x",":",$a[2]??"x",":",$k;'),
 ('reference/key-reference-rhs-rebinds',
  b'<?php $a=[];$j=1;$z=2;$a[($k=&$j)]??=($j=&$z);echo $a[1]??"x",":",$a[2]??"x",":",$k;'),
 ('reference/key-reference-ternary-copy',
  b'<?php $a=[];$j=1;$a[(true?($k=&$j):0)]??=($j=2);echo $a[1]??"x",":",$a[2]??"x",":",$k;'),
 ('reference/key-reference-dim-rhs-mutates',
  b'<?php $a=[];$j=[1];$a[($k=&$j[0])]??=($j[0]=2);echo $a[1]??"x",":",$a[2]??"x",":",$k;'),
 ('reference/name-reference-rhs-mutates',
  b'<?php $j="a";${($k=&$j)}??=($j="b");echo $a??"x",":",$b??"x",":",$k;'),
 ('reference/name-reference-rhs-rebinds',
  b'<?php $j="a";$z="b";${($k=&$j)}??=($j=&$z);echo $a??"x",":",$b??"x",":",$k;'),
 ('reference/name-reference-ternary-copy',
  b'<?php $j="a";${(true?($k=&$j):0)}??=($j="b");echo $a??"x",":",$b??"x",":",$k;'),
 ('reference/key-reference-nonnull-cleanup',
  b'<?php $a=[1=>8];$j=1;echo $a[($k=&$j)]??=($j=2);$k=3;echo ":",$j;'),
 ('reference/key-reference-rhs-type-change', b'<?php $a=[];$j=1;$a[($k=&$j)]??=($j=[]);'),
 ('reference/key-temp-rhs-type-change', b'<?php $a=[];$j=1;$a[$j+0]??=($j=[]);echo $a[1][0]??"x";'),
 ('reference/nested-reference-key',
  b'<?php $a=[];$j=1;$n=3;$a[($k=&$j)][$n]??=($j=$n=2);echo $a[1][3]??"x",":",$a[2][2]??"x";'),
 ('reference/key-reference-rhs-throw', b'<?php $a=[];$j=1;$a[($k=&$j)]??=(1/0);')]

BOUNDARIES = [('dual-line/float-key-constant',
  b'<?php $a=[];\n$a[1.2+\n0] ??=\n7;',
  ['$ppmemo_at(P.EXPRESSIONS, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = ((3, eps))',
   'P.LOCATION.LINE = 2',
   'P.WRITES = [([PCINDEX 1, PCFIELD 0, PCFIELD 0] ++ [PCFIELD 0], 2), ([PCINDEX 1, PCFIELD 0, PCFIELD 0], 2)]']),
 ('dual-line/float-key-temp',
  b'<?php $a=[];$k=1.2;\n$a[$k+\n0] ??=\n7;',
  ['$ppmemo_at(P.EXPRESSIONS, [PCINDEX 2, PCFIELD 0, PCFIELD 0]) = ((3, eps))',
   'P.LOCATION.LINE = 2',
   'P.WRITES = [([PCINDEX 2, PCFIELD 0, PCFIELD 0] ++ [PCFIELD 0], 2), ([PCINDEX 2, PCFIELD 0, PCFIELD 0], 2)]']),
 ('dual-line/float-key-cv',
  b'<?php $a=[];$k=1.2;\n$a[\n$k] ??=\n7;',
  ['$ppmemo_at(P.EXPRESSIONS, [PCINDEX 2, PCFIELD 0, PCFIELD 0]) = ((3, eps))',
   'P.LOCATION.LINE = 3',
   'P.WRITES = [([PCINDEX 2, PCFIELD 0, PCFIELD 0] ++ [PCFIELD 0], 2), ([PCINDEX 2, PCFIELD 0, PCFIELD 0], 3)]']),
 ('dual-line/float-key-nullbase',
  b'<?php $a=null;\n$a[1.2+\n0] ??=\n7;',
  ['$ppmemo_at(P.EXPRESSIONS, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = ((3, eps))',
   'P.LOCATION.LINE = 2',
   'P.WRITES = [([PCINDEX 1, PCFIELD 0, PCFIELD 0] ++ [PCFIELD 0], 2), ([PCINDEX 1, PCFIELD 0, PCFIELD 0], 2)]']),
 ('dual-line/float-key-falsebase',
  b'<?php $a=false;\n$a[1.2+\n0] ??=\n7;',
  ['$ppmemo_at(P.EXPRESSIONS, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = ((3, eps))',
   'P.LOCATION.LINE = 2',
   'P.WRITES = [([PCINDEX 1, PCFIELD 0, PCFIELD 0] ++ [PCFIELD 0], 2), ([PCINDEX 1, PCFIELD 0, PCFIELD 0], 2)]']),
 ('dual-line/float-key-truebase',
  b'<?php $a=true;\n$a[1.2+\n0] ??=\n7;',
  ['$ppmemo_at(P.EXPRESSIONS, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = ((3, eps))',
   'P.LOCATION.LINE = 2',
   'P.WRITES = [([PCINDEX 1, PCFIELD 0, PCFIELD 0] ++ [PCFIELD 0], 2), ([PCINDEX 1, PCFIELD 0, PCFIELD 0], 2)]']),
 ('dual-line/float-key-selected',
  b'<?php $a=[1=>8];\n$a[1.2+\n0] ??=\n7;',
  ['$ppmemo_at(P.EXPRESSIONS, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = ((3, eps))',
   'P.LOCATION.LINE = 2',
   'P.WRITES = [([PCINDEX 1, PCFIELD 0, PCFIELD 0] ++ [PCFIELD 0], 2), ([PCINDEX 1, PCFIELD 0, PCFIELD 0], 2)]']),
 ('dual-line/float-key-throwrhs',
  b'<?php $a=[];\n$a[1.2+\n0] ??=\n1/0;',
  ['$ppmemo_at(P.EXPRESSIONS, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = ((3, eps))',
   'P.LOCATION.LINE = 2',
   'P.WRITES = [([PCINDEX 1, PCFIELD 0, PCFIELD 0] ++ [PCFIELD 0], 2), ([PCINDEX 1, PCFIELD 0, PCFIELD 0], 2)]']),
 ('dual-line/nested-falsebase',
  b'<?php $a=false;\n$a[1.2+\n0][2.3+\n0] ??=\n7;',
  ['$ppmemo_at(P.EXPRESSIONS, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = ((4, eps))',
   'P.LOCATION.LINE = 3',
   'P.WRITES = [([PCINDEX 1, PCFIELD 0, PCFIELD 0] ++ [PCFIELD 0, PCFIELD 0], 2), ([PCINDEX 1, PCFIELD 0, PCFIELD 0] ++ [PCFIELD '
   '0], 2), ([PCINDEX 1, PCFIELD 0, PCFIELD 0], 3)]']),
 ('dual-line/nested-truebase',
  b'<?php $a=true;\n$a[1.2+\n0][2.3+\n0] ??=\n7;',
  ['$ppmemo_at(P.EXPRESSIONS, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = ((4, eps))',
   'P.LOCATION.LINE = 3',
   'P.WRITES = [([PCINDEX 1, PCFIELD 0, PCFIELD 0] ++ [PCFIELD 0, PCFIELD 0], 2), ([PCINDEX 1, PCFIELD 0, PCFIELD 0] ++ [PCFIELD '
   '0], 2), ([PCINDEX 1, PCFIELD 0, PCFIELD 0], 3)]']),
 ('dual-line/nested-arraybase',
  b'<?php $a=[];\n$a[1.2+\n0][2.3+\n0] ??=\n7;',
  ['$ppmemo_at(P.EXPRESSIONS, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = ((4, eps))',
   'P.LOCATION.LINE = 3',
   'P.WRITES = [([PCINDEX 1, PCFIELD 0, PCFIELD 0] ++ [PCFIELD 0, PCFIELD 0], 2), ([PCINDEX 1, PCFIELD 0, PCFIELD 0] ++ [PCFIELD '
   '0], 2), ([PCINDEX 1, PCFIELD 0, PCFIELD 0], 3)]']),
 ('dual-line/key-array-early',
  b'<?php $a=[];\n$a[[]] ??=\n1/0;',
  ['$ppmemo_at(P.EXPRESSIONS, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = ((2, eps))',
   'P.LOCATION.LINE = 2',
   'P.WRITES = [([PCINDEX 1, PCFIELD 0, PCFIELD 0] ++ [PCFIELD 0], 2), ([PCINDEX 1, PCFIELD 0, PCFIELD 0], 2)]']),
 ('dual-line/name-this-cv',
  b'<?php $n="this";\n${\n$n} ??=\n7;',
  ['$ppmemo_at(P.EXPRESSIONS, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = ((3, eps))',
   'P.LOCATION.LINE = 3',
   'P.WRITES = [([PCINDEX 1, PCFIELD 0, PCFIELD 0], 3)]']),
 ('dual-line/name-this-temp',
  b'<?php $n="this";\n${"".\n$n} ??=\n7;',
  ['$ppmemo_at(P.EXPRESSIONS, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = ((3, eps))',
   'P.LOCATION.LINE = 2',
   'P.WRITES = [([PCINDEX 1, PCFIELD 0, PCFIELD 0], 2)]']),
 ('dual-line/name-this-cast',
  b'<?php $n="this";\n${(string)\n$n} ??=\n7;',
  ['$ppmemo_at(P.EXPRESSIONS, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = ((3, eps))',
   'P.LOCATION.LINE = 3',
   'P.WRITES = [([PCINDEX 1, PCFIELD 0, PCFIELD 0], 3)]']),
 ('dual-line/name-globals-temp',
  b'<?php $n="GLOBALS";\n${"".\n$n} ??=\n7;',
  ['$ppmemo_at(P.EXPRESSIONS, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = ((3, eps))',
   'P.LOCATION.LINE = 2',
   'P.WRITES = [([PCINDEX 1, PCFIELD 0, PCFIELD 0], 2)]']),
 ('dual-line/key-undefined-cv',
  b'<?php $a=[];\n$a[\n$k] ??=\n7;',
  ['$ppmemo_at(P.EXPRESSIONS, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = ((3, eps))',
   'P.LOCATION.LINE = 3',
   'P.WRITES = [([PCINDEX 1, PCFIELD 0, PCFIELD 0] ++ [PCFIELD 0], 2), ([PCINDEX 1, PCFIELD 0, PCFIELD 0], 3)]']),
 ('dual-line/key-undefined-temp',
  b'<?php $a=[];\n$a[$k+\n0] ??=\n7;',
  ['$ppmemo_at(P.EXPRESSIONS, [PCINDEX 1, PCFIELD 0, PCFIELD 0]) = ((3, eps))',
   'P.LOCATION.LINE = 2',
   'P.WRITES = [([PCINDEX 1, PCFIELD 0, PCFIELD 0] ++ [PCFIELD 0], 2), ([PCINDEX 1, PCFIELD 0, PCFIELD 0], 2)]']),
 ('dual-line/name-undefined-cv',
  b'<?php ${\n$n} ??=\n7;',
  ['$ppmemo_at(P.EXPRESSIONS, [PCINDEX 0, PCFIELD 0, PCFIELD 0]) = ((2, eps))',
   'P.LOCATION.LINE = 2',
   'P.WRITES = [([PCINDEX 0, PCFIELD 0, PCFIELD 0], 2)]']),
 ('dual-line/name-undefined-temp',
  b'<?php ${"".\n$n} ??=\n7;',
  ['$ppmemo_at(P.EXPRESSIONS, [PCINDEX 0, PCFIELD 0, PCFIELD 0]) = ((2, eps))',
   'P.LOCATION.LINE = 1',
   'P.WRITES = [([PCINDEX 0, PCFIELD 0, PCFIELD 0], 1)]']),
 ('direct-header', b'<?php $http_response_header??=1;', ['P.HEADERASSIGNED = true']),
 ('effect-key-once',
  b'<?php $a[(list($k)=[1])[0]]??=7;',
  ['$quiet_effect(P.EXPRESSIONS, [PCINDEX 0, PCFIELD 0, PCFIELD 0, PCFIELD 1, PCFIELD 0])',
   '$ppaccess(P, [PCINDEX 0, PCFIELD 0, PCFIELD 0]) = (PPIS)',
   '$ppmemo_at(P.EXPRESSIONS, [PCINDEX 0, PCFIELD 0]) = ((1, eps))'])]

PREFIX = compiler.PREFIX + r"""
dec $quiet_effect(ppexprdone*, pcpath) : bool
def $quiet_effect(eps, pcpath) = false
def $quiet_effect((PPCEFFECT pcpath) :: ppexprdone*, pcpath) = true
def $quiet_effect((PPCEFFECT pcpath_other) :: ppexprdone*, pcpath) = $quiet_effect(ppexprdone*, pcpath)
  -- if pcpath_other =/= pcpath
def $quiet_effect((PPCEXPR pcpath_other n pvalue?) :: ppexprdone*, pcpath) = $quiet_effect(ppexprdone*, pcpath)
"""

MALFORMED = '  -- if P_0 = $ppmemo(P[.EXPRESSIONS = eps], ([PCINDEX 0]), (NScalarInt ((INTEGER (1))) ([(MstartLine (1))])))\n  -- if P_0.COMPLETION = PPCABRUPT (UNSUPPORTED "missing memoized operand descriptor")\n  -- if P_1 = $ppmemo(P[.EXPRESSIONS = [PPCEXPR ([PCINDEX 0]) 0 eps]], ([PCINDEX 0]), (NScalarInt ((INTEGER (1))) ([(MstartLine (1))])))\n  -- if P_1.COMPLETION = PPCABRUPT (UNSUPPORTED "missing memoized operand line")\n  -- if P_2 = $ppmemo(P[.EXPRESSIONS = [PPCEFFECT ([PCINDEX 1]), PPCEXPR ([PCINDEX 0]) 1 (PINT 3)]], ([PCINDEX 0]), (NScalarInt ((INTEGER (1))) ([(MstartLine (1))])))\n  -- if P_2.FOLD.VALUE = (PINT 3)\n  -- if P_3 = $ppmemo(P[.EXPRESSIONS = [PPCEXPR ([PCINDEX 0]) 1 eps]], ([PCINDEX 0]), (NScalarInt ((INTEGER (1))) ([(MstartLine (0))])))\n  -- if P_3.COMPLETION = PPCABRUPT (UNSUPPORTED "missing ordinary compiler line")\n  -- if P_4 = $ppwritedone(P[.WRITES = eps][.ACCESS = [(([PCINDEX 0]), PPIS)]][.LOCATION.LINE = 1], ([PCINDEX 0]))\n  -- if P_4.WRITES = [(([PCINDEX 0]), 1)]\n  -- if P_5 = $ppwritedone(P[.WRITES = eps][.ACCESS = [(([PCINDEX 0]), PPIS)]][.LOCATION.LINE = 1][.WRITES = [(([PCINDEX 0]), 1)]], ([PCINDEX 0]))\n  -- if P_5.COMPLETION = PPCABRUPT (UNSUPPORTED "invalid memoized write descriptor")\n  -- if P_6 = $ppwritedone(P[.WRITES = eps][.ACCESS = [(([PCINDEX 0]), PPIS)]][.LOCATION.LINE = 1][.ACCESS = [(([PCINDEX 0]), PPR)]], ([PCINDEX 0]))\n  -- if P_6.COMPLETION = PPCABRUPT (UNSUPPORTED "invalid memoized write descriptor")\n  -- if P_7 = $ppwritedone(P[.WRITES = eps][.ACCESS = [(([PCINDEX 0]), PPIS)]][.LOCATION.LINE = 1][.LOCATION.LINE = 0], ([PCINDEX 0]))\n  -- if P_7.COMPLETION = PPCABRUPT (UNSUPPORTED "invalid memoized write descriptor")\n'

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
        with tempfile.TemporaryDirectory(prefix='php-coalesce-assignment-compiler-',dir=ROOT/'.tools') as directory:
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
            path=work/'malformed.php';path.write_bytes(b'<?php $a=[]; $a[1]??=7;')
            add(checked(path.read_bytes()),path,['P.COMPLETION = PPCNORMAL'])
            fixtures[-1]+=MALFORMED
            fixture=work/'check.watsup';fixture.write_text(PREFIX+'\n'.join(fixtures)+'\ndec $main() : bool\ndef $main() = true\n'+''.join(f'  -- if $case{i}()\n' for i in range(len(fixtures))))
            run=subprocess.run([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),*map(str,compiler.SPECS),str(fixture)],capture_output=True,text=True,timeout=180)
            if run.returncode!=0 or run.stdout.strip()!='true':
                failure=Path(tempfile.mkdtemp(prefix='coalesce-assignment-compiler-failure-',dir=ROOT/'.tools'))
                (failure/'results.json').write_text(json.dumps({'fingerprint':before,'records':records,'boundaries':boundaries,'fixture':fixture.read_text(),'status':run.returncode,'stdout':run.stdout,'stderr':run.stderr},indent=2)+'\n')
                raise AssertionError((str(failure),run.stdout,run.stderr))
    finally:
        frontend.close();adapter.close()
    assert before==inputs(),'inputs changed during coalescing assignment compiler checks'
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({'scope':'84 exact compiler traces,22 read/write/effect controls and8 malformed memoization/write descriptor controls; runtime source execution tested separately','fingerprint':before,'profile':types.PROFILE,'records':records,'boundaries':boundaries,'malformed_assertions':8},indent=2)+'\n')
    print('Coalescing assignment compiler: 84 native lints,22 source descriptor controls and8 malformed state controls passed')

if __name__=='__main__':
    main()
