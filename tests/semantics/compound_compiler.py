#!/usr/bin/env python3
"""Compound compiler barriers, rejection order, access and delayed opcode lines."""
import base64,copy,hashlib,json,subprocess,tempfile
from pathlib import Path
import source_compiler as compiler
from source_compiler import ROOT,types,context,occurrences

CASES={
    '+=/$x/1': b'<?php use A; $x += 1; use B;',
    '+=/$x/[&$q[]]': b'<?php use A; $x += [&$q[]]; use B;',
    '+=/$a[]/1': b'<?php use A; $a[] += 1; use B;',
    '+=/$a[]/[&$q[]]': b'<?php use A; $a[] += [&$q[]]; use B;',
    '+=/foo()/1': b'<?php use A; foo() += 1; use B;',
    '+=/foo()/[&$q[]]': b'<?php use A; foo() += [&$q[]]; use B;',
    '+=/$o?->p/1': b'<?php use A; $o?->p += 1; use B;',
    '+=/$o?->p/[&$q[]]': b'<?php use A; $o?->p += [&$q[]]; use B;',
    '+=/$this/1': b'<?php use A; $this += 1; use B;',
    '+=/$this/[&$q[]]': b'<?php use A; $this += [&$q[]]; use B;',
    '+=/${"this"}/1': b'<?php use A; ${"this"} += 1; use B;',
    '+=/${"this"}/[&$q[]]': b'<?php use A; ${"this"} += [&$q[]]; use B;',
    'deep-+=-false': b'<?php use A; echo [false && ($a += [[[]=>1]])][0]; use B;',
    'deep-+=-true': b'<?php use A; echo [true && ($a += [[[]=>1]])][0]; use B;',
    'array-value-+=': b'<?php $a=1;$b=[($a += 1)];echo $b[0];',
    'array-key-+=': b'<?php $a=1;$b=[($a += 1)=>2];echo $a;',
    '-=/$x/1': b'<?php use A; $x -= 1; use B;',
    '-=/$x/[&$q[]]': b'<?php use A; $x -= [&$q[]]; use B;',
    '-=/$a[]/1': b'<?php use A; $a[] -= 1; use B;',
    '-=/$a[]/[&$q[]]': b'<?php use A; $a[] -= [&$q[]]; use B;',
    '-=/foo()/1': b'<?php use A; foo() -= 1; use B;',
    '-=/foo()/[&$q[]]': b'<?php use A; foo() -= [&$q[]]; use B;',
    '-=/$o?->p/1': b'<?php use A; $o?->p -= 1; use B;',
    '-=/$o?->p/[&$q[]]': b'<?php use A; $o?->p -= [&$q[]]; use B;',
    '-=/$this/1': b'<?php use A; $this -= 1; use B;',
    '-=/$this/[&$q[]]': b'<?php use A; $this -= [&$q[]]; use B;',
    '-=/${"this"}/1': b'<?php use A; ${"this"} -= 1; use B;',
    '-=/${"this"}/[&$q[]]': b'<?php use A; ${"this"} -= [&$q[]]; use B;',
    'deep--=-false': b'<?php use A; echo [false && ($a -= [[[]=>1]])][0]; use B;',
    'deep--=-true': b'<?php use A; echo [true && ($a -= [[[]=>1]])][0]; use B;',
    'array-value--=': b'<?php $a=1;$b=[($a -= 1)];echo $b[0];',
    'array-key--=': b'<?php $a=1;$b=[($a -= 1)=>2];echo $a;',
    '*=/$x/1': b'<?php use A; $x *= 1; use B;',
    '*=/$x/[&$q[]]': b'<?php use A; $x *= [&$q[]]; use B;',
    '*=/$a[]/1': b'<?php use A; $a[] *= 1; use B;',
    '*=/$a[]/[&$q[]]': b'<?php use A; $a[] *= [&$q[]]; use B;',
    '*=/foo()/1': b'<?php use A; foo() *= 1; use B;',
    '*=/foo()/[&$q[]]': b'<?php use A; foo() *= [&$q[]]; use B;',
    '*=/$o?->p/1': b'<?php use A; $o?->p *= 1; use B;',
    '*=/$o?->p/[&$q[]]': b'<?php use A; $o?->p *= [&$q[]]; use B;',
    '*=/$this/1': b'<?php use A; $this *= 1; use B;',
    '*=/$this/[&$q[]]': b'<?php use A; $this *= [&$q[]]; use B;',
    '*=/${"this"}/1': b'<?php use A; ${"this"} *= 1; use B;',
    '*=/${"this"}/[&$q[]]': b'<?php use A; ${"this"} *= [&$q[]]; use B;',
    'deep-*=-false': b'<?php use A; echo [false && ($a *= [[[]=>1]])][0]; use B;',
    'deep-*=-true': b'<?php use A; echo [true && ($a *= [[[]=>1]])][0]; use B;',
    'array-value-*=': b'<?php $a=1;$b=[($a *= 1)];echo $b[0];',
    'array-key-*=': b'<?php $a=1;$b=[($a *= 1)=>2];echo $a;',
    '/=/$x/1': b'<?php use A; $x /= 1; use B;',
    '/=/$x/[&$q[]]': b'<?php use A; $x /= [&$q[]]; use B;',
    '/=/$a[]/1': b'<?php use A; $a[] /= 1; use B;',
    '/=/$a[]/[&$q[]]': b'<?php use A; $a[] /= [&$q[]]; use B;',
    '/=/foo()/1': b'<?php use A; foo() /= 1; use B;',
    '/=/foo()/[&$q[]]': b'<?php use A; foo() /= [&$q[]]; use B;',
    '/=/$o?->p/1': b'<?php use A; $o?->p /= 1; use B;',
    '/=/$o?->p/[&$q[]]': b'<?php use A; $o?->p /= [&$q[]]; use B;',
    '/=/$this/1': b'<?php use A; $this /= 1; use B;',
    '/=/$this/[&$q[]]': b'<?php use A; $this /= [&$q[]]; use B;',
    '/=/${"this"}/1': b'<?php use A; ${"this"} /= 1; use B;',
    '/=/${"this"}/[&$q[]]': b'<?php use A; ${"this"} /= [&$q[]]; use B;',
    'deep-/=-false': b'<?php use A; echo [false && ($a /= [[[]=>1]])][0]; use B;',
    'deep-/=-true': b'<?php use A; echo [true && ($a /= [[[]=>1]])][0]; use B;',
    'array-value-/=': b'<?php $a=1;$b=[($a /= 1)];echo $b[0];',
    'array-key-/=': b'<?php $a=1;$b=[($a /= 1)=>2];echo $a;',
    '%=/$x/1': b'<?php use A; $x %= 1; use B;',
    '%=/$x/[&$q[]]': b'<?php use A; $x %= [&$q[]]; use B;',
    '%=/$a[]/1': b'<?php use A; $a[] %= 1; use B;',
    '%=/$a[]/[&$q[]]': b'<?php use A; $a[] %= [&$q[]]; use B;',
    '%=/foo()/1': b'<?php use A; foo() %= 1; use B;',
    '%=/foo()/[&$q[]]': b'<?php use A; foo() %= [&$q[]]; use B;',
    '%=/$o?->p/1': b'<?php use A; $o?->p %= 1; use B;',
    '%=/$o?->p/[&$q[]]': b'<?php use A; $o?->p %= [&$q[]]; use B;',
    '%=/$this/1': b'<?php use A; $this %= 1; use B;',
    '%=/$this/[&$q[]]': b'<?php use A; $this %= [&$q[]]; use B;',
    '%=/${"this"}/1': b'<?php use A; ${"this"} %= 1; use B;',
    '%=/${"this"}/[&$q[]]': b'<?php use A; ${"this"} %= [&$q[]]; use B;',
    'deep-%=-false': b'<?php use A; echo [false && ($a %= [[[]=>1]])][0]; use B;',
    'deep-%=-true': b'<?php use A; echo [true && ($a %= [[[]=>1]])][0]; use B;',
    'array-value-%=': b'<?php $a=1;$b=[($a %= 1)];echo $b[0];',
    'array-key-%=': b'<?php $a=1;$b=[($a %= 1)=>2];echo $a;',
    '**=/$x/1': b'<?php use A; $x **= 1; use B;',
    '**=/$x/[&$q[]]': b'<?php use A; $x **= [&$q[]]; use B;',
    '**=/$a[]/1': b'<?php use A; $a[] **= 1; use B;',
    '**=/$a[]/[&$q[]]': b'<?php use A; $a[] **= [&$q[]]; use B;',
    '**=/foo()/1': b'<?php use A; foo() **= 1; use B;',
    '**=/foo()/[&$q[]]': b'<?php use A; foo() **= [&$q[]]; use B;',
    '**=/$o?->p/1': b'<?php use A; $o?->p **= 1; use B;',
    '**=/$o?->p/[&$q[]]': b'<?php use A; $o?->p **= [&$q[]]; use B;',
    '**=/$this/1': b'<?php use A; $this **= 1; use B;',
    '**=/$this/[&$q[]]': b'<?php use A; $this **= [&$q[]]; use B;',
    '**=/${"this"}/1': b'<?php use A; ${"this"} **= 1; use B;',
    '**=/${"this"}/[&$q[]]': b'<?php use A; ${"this"} **= [&$q[]]; use B;',
    'deep-**=-false': b'<?php use A; echo [false && ($a **= [[[]=>1]])][0]; use B;',
    'deep-**=-true': b'<?php use A; echo [true && ($a **= [[[]=>1]])][0]; use B;',
    'array-value-**=': b'<?php $a=1;$b=[($a **= 1)];echo $b[0];',
    'array-key-**=': b'<?php $a=1;$b=[($a **= 1)=>2];echo $a;',
    '<<=/$x/1': b'<?php use A; $x <<= 1; use B;',
    '<<=/$x/[&$q[]]': b'<?php use A; $x <<= [&$q[]]; use B;',
    '<<=/$a[]/1': b'<?php use A; $a[] <<= 1; use B;',
    '<<=/$a[]/[&$q[]]': b'<?php use A; $a[] <<= [&$q[]]; use B;',
    '<<=/foo()/1': b'<?php use A; foo() <<= 1; use B;',
    '<<=/foo()/[&$q[]]': b'<?php use A; foo() <<= [&$q[]]; use B;',
    '<<=/$o?->p/1': b'<?php use A; $o?->p <<= 1; use B;',
    '<<=/$o?->p/[&$q[]]': b'<?php use A; $o?->p <<= [&$q[]]; use B;',
    '<<=/$this/1': b'<?php use A; $this <<= 1; use B;',
    '<<=/$this/[&$q[]]': b'<?php use A; $this <<= [&$q[]]; use B;',
    '<<=/${"this"}/1': b'<?php use A; ${"this"} <<= 1; use B;',
    '<<=/${"this"}/[&$q[]]': b'<?php use A; ${"this"} <<= [&$q[]]; use B;',
    'deep-<<=-false': b'<?php use A; echo [false && ($a <<= [[[]=>1]])][0]; use B;',
    'deep-<<=-true': b'<?php use A; echo [true && ($a <<= [[[]=>1]])][0]; use B;',
    'array-value-<<=': b'<?php $a=1;$b=[($a <<= 1)];echo $b[0];',
    'array-key-<<=': b'<?php $a=1;$b=[($a <<= 1)=>2];echo $a;',
    '>>=/$x/1': b'<?php use A; $x >>= 1; use B;',
    '>>=/$x/[&$q[]]': b'<?php use A; $x >>= [&$q[]]; use B;',
    '>>=/$a[]/1': b'<?php use A; $a[] >>= 1; use B;',
    '>>=/$a[]/[&$q[]]': b'<?php use A; $a[] >>= [&$q[]]; use B;',
    '>>=/foo()/1': b'<?php use A; foo() >>= 1; use B;',
    '>>=/foo()/[&$q[]]': b'<?php use A; foo() >>= [&$q[]]; use B;',
    '>>=/$o?->p/1': b'<?php use A; $o?->p >>= 1; use B;',
    '>>=/$o?->p/[&$q[]]': b'<?php use A; $o?->p >>= [&$q[]]; use B;',
    '>>=/$this/1': b'<?php use A; $this >>= 1; use B;',
    '>>=/$this/[&$q[]]': b'<?php use A; $this >>= [&$q[]]; use B;',
    '>>=/${"this"}/1': b'<?php use A; ${"this"} >>= 1; use B;',
    '>>=/${"this"}/[&$q[]]': b'<?php use A; ${"this"} >>= [&$q[]]; use B;',
    'deep->>=-false': b'<?php use A; echo [false && ($a >>= [[[]=>1]])][0]; use B;',
    'deep->>=-true': b'<?php use A; echo [true && ($a >>= [[[]=>1]])][0]; use B;',
    'array-value->>=': b'<?php $a=1;$b=[($a >>= 1)];echo $b[0];',
    'array-key->>=': b'<?php $a=1;$b=[($a >>= 1)=>2];echo $a;',
    '&=/$x/1': b'<?php use A; $x &= 1; use B;',
    '&=/$x/[&$q[]]': b'<?php use A; $x &= [&$q[]]; use B;',
    '&=/$a[]/1': b'<?php use A; $a[] &= 1; use B;',
    '&=/$a[]/[&$q[]]': b'<?php use A; $a[] &= [&$q[]]; use B;',
    '&=/foo()/1': b'<?php use A; foo() &= 1; use B;',
    '&=/foo()/[&$q[]]': b'<?php use A; foo() &= [&$q[]]; use B;',
    '&=/$o?->p/1': b'<?php use A; $o?->p &= 1; use B;',
    '&=/$o?->p/[&$q[]]': b'<?php use A; $o?->p &= [&$q[]]; use B;',
    '&=/$this/1': b'<?php use A; $this &= 1; use B;',
    '&=/$this/[&$q[]]': b'<?php use A; $this &= [&$q[]]; use B;',
    '&=/${"this"}/1': b'<?php use A; ${"this"} &= 1; use B;',
    '&=/${"this"}/[&$q[]]': b'<?php use A; ${"this"} &= [&$q[]]; use B;',
    'deep-&=-false': b'<?php use A; echo [false && ($a &= [[[]=>1]])][0]; use B;',
    'deep-&=-true': b'<?php use A; echo [true && ($a &= [[[]=>1]])][0]; use B;',
    'array-value-&=': b'<?php $a=1;$b=[($a &= 1)];echo $b[0];',
    'array-key-&=': b'<?php $a=1;$b=[($a &= 1)=>2];echo $a;',
    '|=/$x/1': b'<?php use A; $x |= 1; use B;',
    '|=/$x/[&$q[]]': b'<?php use A; $x |= [&$q[]]; use B;',
    '|=/$a[]/1': b'<?php use A; $a[] |= 1; use B;',
    '|=/$a[]/[&$q[]]': b'<?php use A; $a[] |= [&$q[]]; use B;',
    '|=/foo()/1': b'<?php use A; foo() |= 1; use B;',
    '|=/foo()/[&$q[]]': b'<?php use A; foo() |= [&$q[]]; use B;',
    '|=/$o?->p/1': b'<?php use A; $o?->p |= 1; use B;',
    '|=/$o?->p/[&$q[]]': b'<?php use A; $o?->p |= [&$q[]]; use B;',
    '|=/$this/1': b'<?php use A; $this |= 1; use B;',
    '|=/$this/[&$q[]]': b'<?php use A; $this |= [&$q[]]; use B;',
    '|=/${"this"}/1': b'<?php use A; ${"this"} |= 1; use B;',
    '|=/${"this"}/[&$q[]]': b'<?php use A; ${"this"} |= [&$q[]]; use B;',
    'deep-|=-false': b'<?php use A; echo [false && ($a |= [[[]=>1]])][0]; use B;',
    'deep-|=-true': b'<?php use A; echo [true && ($a |= [[[]=>1]])][0]; use B;',
    'array-value-|=': b'<?php $a=1;$b=[($a |= 1)];echo $b[0];',
    'array-key-|=': b'<?php $a=1;$b=[($a |= 1)=>2];echo $a;',
    '^=/$x/1': b'<?php use A; $x ^= 1; use B;',
    '^=/$x/[&$q[]]': b'<?php use A; $x ^= [&$q[]]; use B;',
    '^=/$a[]/1': b'<?php use A; $a[] ^= 1; use B;',
    '^=/$a[]/[&$q[]]': b'<?php use A; $a[] ^= [&$q[]]; use B;',
    '^=/foo()/1': b'<?php use A; foo() ^= 1; use B;',
    '^=/foo()/[&$q[]]': b'<?php use A; foo() ^= [&$q[]]; use B;',
    '^=/$o?->p/1': b'<?php use A; $o?->p ^= 1; use B;',
    '^=/$o?->p/[&$q[]]': b'<?php use A; $o?->p ^= [&$q[]]; use B;',
    '^=/$this/1': b'<?php use A; $this ^= 1; use B;',
    '^=/$this/[&$q[]]': b'<?php use A; $this ^= [&$q[]]; use B;',
    '^=/${"this"}/1': b'<?php use A; ${"this"} ^= 1; use B;',
    '^=/${"this"}/[&$q[]]': b'<?php use A; ${"this"} ^= [&$q[]]; use B;',
    'deep-^=-false': b'<?php use A; echo [false && ($a ^= [[[]=>1]])][0]; use B;',
    'deep-^=-true': b'<?php use A; echo [true && ($a ^= [[[]=>1]])][0]; use B;',
    'array-value-^=': b'<?php $a=1;$b=[($a ^= 1)];echo $b[0];',
    'array-key-^=': b'<?php $a=1;$b=[($a ^= 1)=>2];echo $a;',
    '.=/$x/1': b'<?php use A; $x .= 1; use B;',
    '.=/$x/[&$q[]]': b'<?php use A; $x .= [&$q[]]; use B;',
    '.=/$a[]/1': b'<?php use A; $a[] .= 1; use B;',
    '.=/$a[]/[&$q[]]': b'<?php use A; $a[] .= [&$q[]]; use B;',
    '.=/foo()/1': b'<?php use A; foo() .= 1; use B;',
    '.=/foo()/[&$q[]]': b'<?php use A; foo() .= [&$q[]]; use B;',
    '.=/$o?->p/1': b'<?php use A; $o?->p .= 1; use B;',
    '.=/$o?->p/[&$q[]]': b'<?php use A; $o?->p .= [&$q[]]; use B;',
    '.=/$this/1': b'<?php use A; $this .= 1; use B;',
    '.=/$this/[&$q[]]': b'<?php use A; $this .= [&$q[]]; use B;',
    '.=/${"this"}/1': b'<?php use A; ${"this"} .= 1; use B;',
    '.=/${"this"}/[&$q[]]': b'<?php use A; ${"this"} .= [&$q[]]; use B;',
    'deep-.=-false': b'<?php use A; echo [false && ($a .= [[[]=>1]])][0]; use B;',
    'deep-.=-true': b'<?php use A; echo [true && ($a .= [[[]=>1]])][0]; use B;',
    'array-value-.=': b'<?php $a=1;$b=[($a .= 1)];echo $b[0];',
    'array-key-.=': b'<?php $a=1;$b=[($a .= 1)=>2];echo $a;',
    'retained-this-4': b'<?php use A; ${true?"this":"other"} += 1; use B;',
    'retained-this-5': b'<?php use A; ${true?"this":"other"} += [&$q[]]; use B;',
    'retained-this-10': b'<?php use A; ${true?"this":"other"} -= 1; use B;',
    'retained-this-11': b'<?php use A; ${true?"this":"other"} -= [&$q[]]; use B;',
    'retained-this-16': b'<?php use A; ${true?"this":"other"} *= 1; use B;',
    'retained-this-17': b'<?php use A; ${true?"this":"other"} *= [&$q[]]; use B;',
    'retained-this-22': b'<?php use A; ${true?"this":"other"} /= 1; use B;',
    'retained-this-23': b'<?php use A; ${true?"this":"other"} /= [&$q[]]; use B;',
    'retained-this-28': b'<?php use A; ${true?"this":"other"} %= 1; use B;',
    'retained-this-29': b'<?php use A; ${true?"this":"other"} %= [&$q[]]; use B;',
    'retained-this-34': b'<?php use A; ${true?"this":"other"} **= 1; use B;',
    'retained-this-35': b'<?php use A; ${true?"this":"other"} **= [&$q[]]; use B;',
    'retained-this-40': b'<?php use A; ${true?"this":"other"} .= 1; use B;',
    'retained-this-41': b'<?php use A; ${true?"this":"other"} .= [&$q[]]; use B;',
    'retained-this-46': b'<?php use A; ${true?"this":"other"} &= 1; use B;',
    'retained-this-47': b'<?php use A; ${true?"this":"other"} &= [&$q[]]; use B;',
    'retained-this-52': b'<?php use A; ${true?"this":"other"} |= 1; use B;',
    'retained-this-53': b'<?php use A; ${true?"this":"other"} |= [&$q[]]; use B;',
    'retained-this-58': b'<?php use A; ${true?"this":"other"} ^= 1; use B;',
    'retained-this-59': b'<?php use A; ${true?"this":"other"} ^= [&$q[]]; use B;',
    'retained-this-64': b'<?php use A; ${true?"this":"other"} <<= 1; use B;',
    'retained-this-65': b'<?php use A; ${true?"this":"other"} <<= [&$q[]]; use B;',
    'retained-this-70': b'<?php use A; ${true?"this":"other"} >>= 1; use B;',
    'retained-this-71': b'<?php use A; ${true?"this":"other"} >>= [&$q[]]; use B;',
    'retained-line-0': b'<?php $a=[1];\necho $a[\n0\n]\n+=\n"2x";',
    'retained-line-1': b'<?php $a=[1];\necho $a[\n0\n]\n+=\n$a;',
    'retained-line-2': b'<?php $a=1;\necho $a\n+=\n"2x";',
    'retained-line-3': b'<?php $a=1;\necho $a\n+=\n$a;',
    'retained-line-4': b'<?php $a=1;$n="a";\necho ${\n$n\n}\n+=\n"2x";',
    'retained-line-5': b'<?php $a=1;$n="a";\necho ${\n$n\n}\n+=\n$a;',
    'retained-line-6': b'<?php $a=[1];\necho $a[\n0\n]\n-=\n"2x";',
    'retained-line-7': b'<?php $a=[1];\necho $a[\n0\n]\n-=\n$a;',
    'retained-line-8': b'<?php $a=1;\necho $a\n-=\n"2x";',
    'retained-line-9': b'<?php $a=1;\necho $a\n-=\n$a;',
    'retained-line-10': b'<?php $a=1;$n="a";\necho ${\n$n\n}\n-=\n"2x";',
    'retained-line-11': b'<?php $a=1;$n="a";\necho ${\n$n\n}\n-=\n$a;',
    'retained-line-12': b'<?php $a=[1];\necho $a[\n0\n]\n*=\n"2x";',
    'retained-line-13': b'<?php $a=[1];\necho $a[\n0\n]\n*=\n$a;',
    'retained-line-14': b'<?php $a=1;\necho $a\n*=\n"2x";',
    'retained-line-15': b'<?php $a=1;\necho $a\n*=\n$a;',
    'retained-line-16': b'<?php $a=1;$n="a";\necho ${\n$n\n}\n*=\n"2x";',
    'retained-line-17': b'<?php $a=1;$n="a";\necho ${\n$n\n}\n*=\n$a;',
    'retained-line-18': b'<?php $a=[1];\necho $a[\n0\n]\n/=\n"2x";',
    'retained-line-19': b'<?php $a=[1];\necho $a[\n0\n]\n/=\n$a;',
    'retained-line-20': b'<?php $a=1;\necho $a\n/=\n"2x";',
    'retained-line-21': b'<?php $a=1;\necho $a\n/=\n$a;',
    'retained-line-22': b'<?php $a=1;$n="a";\necho ${\n$n\n}\n/=\n"2x";',
    'retained-line-23': b'<?php $a=1;$n="a";\necho ${\n$n\n}\n/=\n$a;',
    'retained-line-24': b'<?php $a=[1];\necho $a[\n0\n]\n%=\n"2x";',
    'retained-line-25': b'<?php $a=[1];\necho $a[\n0\n]\n%=\n$a;',
    'retained-line-26': b'<?php $a=1;\necho $a\n%=\n"2x";',
    'retained-line-27': b'<?php $a=1;\necho $a\n%=\n$a;',
    'retained-line-28': b'<?php $a=1;$n="a";\necho ${\n$n\n}\n%=\n"2x";',
    'retained-line-29': b'<?php $a=1;$n="a";\necho ${\n$n\n}\n%=\n$a;',
    'retained-line-30': b'<?php $a=[1];\necho $a[\n0\n]\n**=\n"2x";',
    'retained-line-31': b'<?php $a=[1];\necho $a[\n0\n]\n**=\n$a;',
    'retained-line-32': b'<?php $a=1;\necho $a\n**=\n"2x";',
    'retained-line-33': b'<?php $a=1;\necho $a\n**=\n$a;',
    'retained-line-34': b'<?php $a=1;$n="a";\necho ${\n$n\n}\n**=\n"2x";',
    'retained-line-35': b'<?php $a=1;$n="a";\necho ${\n$n\n}\n**=\n$a;',
    'retained-line-36': b'<?php $a=[1];\necho $a[\n0\n]\n.=\n[];',
    'retained-line-37': b'<?php $a=[1];\necho $a[\n0\n]\n.=\n$a;',
    'retained-line-38': b'<?php $a=1;\necho $a\n.=\n[];',
    'retained-line-39': b'<?php $a=1;\necho $a\n.=\n$a;',
    'retained-line-40': b'<?php $a=1;$n="a";\necho ${\n$n\n}\n.=\n[];',
    'retained-line-41': b'<?php $a=1;$n="a";\necho ${\n$n\n}\n.=\n$a;',
    'retained-line-42': b'<?php $a=[1];\necho $a[\n0\n]\n&=\n"2x";',
    'retained-line-43': b'<?php $a=[1];\necho $a[\n0\n]\n&=\n$a;',
    'retained-line-44': b'<?php $a=1;\necho $a\n&=\n"2x";',
    'retained-line-45': b'<?php $a=1;\necho $a\n&=\n$a;',
    'retained-line-46': b'<?php $a=1;$n="a";\necho ${\n$n\n}\n&=\n"2x";',
    'retained-line-47': b'<?php $a=1;$n="a";\necho ${\n$n\n}\n&=\n$a;',
    'retained-line-48': b'<?php $a=[1];\necho $a[\n0\n]\n|=\n"2x";',
    'retained-line-49': b'<?php $a=[1];\necho $a[\n0\n]\n|=\n$a;',
    'retained-line-50': b'<?php $a=1;\necho $a\n|=\n"2x";',
    'retained-line-51': b'<?php $a=1;\necho $a\n|=\n$a;',
    'retained-line-52': b'<?php $a=1;$n="a";\necho ${\n$n\n}\n|=\n"2x";',
    'retained-line-53': b'<?php $a=1;$n="a";\necho ${\n$n\n}\n|=\n$a;',
    'retained-line-54': b'<?php $a=[1];\necho $a[\n0\n]\n^=\n"2x";',
    'retained-line-55': b'<?php $a=[1];\necho $a[\n0\n]\n^=\n$a;',
    'retained-line-56': b'<?php $a=1;\necho $a\n^=\n"2x";',
    'retained-line-57': b'<?php $a=1;\necho $a\n^=\n$a;',
    'retained-line-58': b'<?php $a=1;$n="a";\necho ${\n$n\n}\n^=\n"2x";',
    'retained-line-59': b'<?php $a=1;$n="a";\necho ${\n$n\n}\n^=\n$a;',
    'retained-line-60': b'<?php $a=[1];\necho $a[\n0\n]\n<<=\n"2x";',
    'retained-line-61': b'<?php $a=[1];\necho $a[\n0\n]\n<<=\n$a;',
    'retained-line-62': b'<?php $a=1;\necho $a\n<<=\n"2x";',
    'retained-line-63': b'<?php $a=1;\necho $a\n<<=\n$a;',
    'retained-line-64': b'<?php $a=1;$n="a";\necho ${\n$n\n}\n<<=\n"2x";',
    'retained-line-65': b'<?php $a=1;$n="a";\necho ${\n$n\n}\n<<=\n$a;',
    'retained-line-66': b'<?php $a=[1];\necho $a[\n0\n]\n>>=\n"2x";',
    'retained-line-67': b'<?php $a=[1];\necho $a[\n0\n]\n>>=\n$a;',
    'retained-line-68': b'<?php $a=1;\necho $a\n>>=\n"2x";',
    'retained-line-69': b'<?php $a=1;\necho $a\n>>=\n$a;',
    'retained-line-70': b'<?php $a=1;$n="a";\necho ${\n$n\n}\n>>=\n"2x";',
    'retained-line-71': b'<?php $a=1;$n="a";\necho ${\n$n\n}\n>>=\n$a;',
    'temporary-write-rhs': b'<?php $a=[1];$b=[2];echo ($a[0] += (($a=&$b)[0]=3));echo $a[0],$b[0];',
}
LINES=[(b'<?php $a=null;\necho ($a +=\n($missing+1));', False), (b'<?php $a=[1];\necho $a[\n0\n] +=\n"2x";', True), (b'<?php $a=null;\necho ($a -=\n($missing+1));', False), (b'<?php $a=[1];\necho $a[\n0\n] -=\n"2x";', True), (b'<?php $a=null;\necho ($a *=\n($missing+1));', False), (b'<?php $a=[1];\necho $a[\n0\n] *=\n"2x";', True), (b'<?php $a=null;\necho ($a /=\n($missing+1));', False), (b'<?php $a=[1];\necho $a[\n0\n] /=\n"2x";', True), (b'<?php $a=null;\necho ($a %=\n($missing+1));', False), (b'<?php $a=[1];\necho $a[\n0\n] %=\n"2x";', True), (b'<?php $a=null;\necho ($a **=\n($missing+1));', False), (b'<?php $a=[1];\necho $a[\n0\n] **=\n"2x";', True), (b'<?php $a=null;\necho ($a <<=\n($missing+1));', False), (b'<?php $a=[1];\necho $a[\n0\n] <<=\n"2x";', True), (b'<?php $a=null;\necho ($a >>=\n($missing+1));', False), (b'<?php $a=[1];\necho $a[\n0\n] >>=\n"2x";', True), (b'<?php $a=null;\necho ($a &=\n($missing+1));', False), (b'<?php $a=[1];\necho $a[\n0\n] &=\n"2x";', True), (b'<?php $a=null;\necho ($a |=\n($missing+1));', False), (b'<?php $a=[1];\necho $a[\n0\n] |=\n"2x";', True), (b'<?php $a=null;\necho ($a ^=\n($missing+1));', False), (b'<?php $a=[1];\necho $a[\n0\n] ^=\n"2x";', True), (b'<?php $a=null;\necho ($a .=\n($missing+1));', False), (b'<?php $a=[1];\necho $a[\n0\n] .=\n[];', True)]


def fingerprint():
    watched=[*compiler.SPECS,Path(__file__),ROOT/'tests/semantics/source_compiler.py',ROOT/'tests/semantics/_build/default/numeric_runner.exe',ROOT/'vendor/php-src/Zend/zend_compile.c']
    return {'closure':types.syntax_validation.implementation_fingerprint(),'direct':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}}


def main():
    subprocess.run([str(ROOT/'scripts/opam-exec.sh'),'dune','build','--root',str(types.HERE),'numeric_runner.exe'],cwd=ROOT,check=True,timeout=120)
    before=fingerprint()
    identity=json.loads(subprocess.run([str(types.PHP),'-n',*types.FLAGS,'-r','echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,ini_get_all(null,false)]);'],capture_output=True,text=True,env=types.ENV,timeout=10,check=True).stdout)
    assert identity[:4]==['8.5.10','cli',8,False]
    assert all(identity[4][k]==v for k,v in types.PROFILE.items())
    I=compiler.I;F=compiler.F
    access_cases=compiler.ACCESS_CASES+[
        (b'<?php $a[0]+=$b;', [([I(0),F(0)],'PPR'),([I(0),F(0),F(0)],'PPRW'),([I(0),F(0),F(0),F(0)],'PPRW'),([I(0),F(0),F(0),F(1)],'PPR'),([I(0),F(0),F(1)],'PPR')]),
        (b'<?php $a[0][]+=$a;', [([I(0),F(0),F(0)],'PPRW'),([I(0),F(0),F(0),F(0)],'PPRW'),([I(0),F(0),F(0),F(0),F(0)],'PPRW'),([I(0),F(0),F(0),F(0),F(1)],'PPR'),([I(0),F(0),F(1)],'PPR')]),
    ]
    f=types.Worker([str(types.PHP),'-n','-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')]);a=types.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    fixtures=[];records=[];roles=[];emissions=[];metadata_checks=[]
    def fixture(ast,checks):
        checked=a.request({'op':'check','ast':ast,'fixture':True});assert checked['ok'],checked
        i=len(fixtures);fixtures.append(f'dec $case{i}() : bool\ndef $case{i}() = true\n  -- if P = $ppstart(74, {checked["fixture"]}, {types.byte_expr(str(file))})\n'+''.join('  -- if '+test+'\n' for test in checks));return checked
    try:
        with tempfile.TemporaryDirectory(dir=ROOT/'.tools') as tmp:
            file=Path(tmp)/'input.php'
            for name,source in CASES.items():
                parsed=f.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
                file.write_bytes(source);command=[str(types.PHP),'-n',*types.FLAGS,'-l',str(file)];run=subprocess.run(command,capture_output=True,cwd=ROOT,env=types.ENV,timeout=10)
                checks=['$pptrace(P) = '+context.expected_events(context.events(run),file),'P.FOLD.WARNINGS = eps']
                if run.returncode==0:checks+=['P.COMPLETION = PPCNORMAL','$access_paths(P.ACCESS) = $expression_paths(P.EXPRESSIONS)']
                checked=fixture(parsed['ast'],checks);records.append({'id':name,'oracle':compiler.oracle_record(source,checked,command,run),'assertions':checks})
            for source,probes in access_cases:
                parsed=f.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
                checks=['P.COMPLETION = PPCNORMAL','$access_paths(P.ACCESS) = $expression_paths(P.EXPRESSIONS)']
                checks += [f'$ppaccess(P, {occurrences.path_term(path)}) = '+('eps' if mode is None else '('+mode+')') for path,mode in probes]
                fixture(parsed['ast'],checks);roles.append({'source_base64':base64.b64encode(source).decode(),'assertions':checks})
            for source,dimension in LINES:
                parsed=f.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
                file.write_bytes(source);command=[str(types.PHP),'-n',*types.FLAGS,str(file)];run=subprocess.run(command,capture_output=True,cwd=ROOT,env=types.ENV,timeout=10)
                assert run.returncode==0,(source,run.stderr)
                events=context.events(run);assert events,source
                line=events[-1][2];path=occurrences.path_term([I(1),F(0),I(0)]+([F(0)] if dimension else []))
                checks=['P.COMPLETION = PPCNORMAL',f'$pprecord(P.EXPRESSIONS, {path}) = (PPCEXPR {path} {line} pvalue?)']
                if dimension:
                    parent=occurrences.path_term([I(1),F(0),I(0)])
                    checks.append(f'$pprecord(P.EXPRESSIONS, {parent}) = (PPCEXPR {parent} 5 pvalue?)')
                checked=fixture(parsed['ast'],checks);emissions.append({'oracle':compiler.oracle_record(source,checked,command,run),'assertions':checks})
            source=b'<?php $f() += 1;'
            parsed=f.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
            for value in [None,'0','-1','17']:
                edited=copy.deepcopy(parsed['ast']);target=edited['program'][0]['fields'][0]['fields'][0]
                if value is None:target['meta'].pop('callableExprLine')
                else:target['meta']['callableExprLine']={'int':value}
                checks=['P.COMPLETION = PPCABRUPT (UNSUPPORTED "missing ordinary compiler line")'] if value!='17' else ['P.COMPLETION = PPCABRUPT (STATICERROR "Can\'t use function return value in write context" 17)']
                fixture(edited,checks);metadata_checks.append({'value':value,'assertions':checks})
            for source in [b'<?php unset($this);', b'<?php $this=1;']:
                parsed=f.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
                for value in [None,'0','-1','17']:
                    edited=copy.deepcopy(parsed['ast']);statement=edited['program'][0]
                    target=statement['fields'][0][0] if statement['node']=='Stmt_Unset' else statement['fields'][0]['fields'][0]
                    if value is None:target['meta'].pop('startLine')
                    else:target['meta']['startLine']={'int':value}
                    message='Cannot unset $this' if statement['node']=='Stmt_Unset' else 'Cannot re-assign $this'
                    checks=['P.COMPLETION = PPCABRUPT (UNSUPPORTED "missing ordinary compiler line")'] if value!='17' else [f'P.COMPLETION = PPCABRUPT (STATICERROR "{message}" 17)']
                    fixture(edited,checks);metadata_checks.append({'source_base64':base64.b64encode(source).decode(),'value':value,'assertions':checks})
            script=Path(tmp)/'checks.watsup';script.write_text(compiler.PREFIX+'\ndec $pprecord(ppexprdone*, pcpath) : ppexprdone?\ndef $pprecord(eps, pcpath) = eps\ndef $pprecord((PPCEFFECT pcpath_effect) :: ppexprdone*, pcpath) = $pprecord(ppexprdone*, pcpath)\ndef $pprecord((PPCEXPR pcpath n pvalue?) :: ppexprdone*, pcpath) = (PPCEXPR pcpath n pvalue?)\ndef $pprecord((PPCEXPR pcpath_other n pvalue?) :: ppexprdone*, pcpath) = $pprecord(ppexprdone*, pcpath)\n  -- if pcpath_other =/= pcpath\n'+'\n'.join(fixtures)+'dec $main() : bool\ndef $main() = true\n'+''.join(f'  -- if $case{i}()\n' for i in range(len(fixtures))))
            run=subprocess.run([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),*map(str,compiler.SPECS),str(script)],capture_output=True,text=True,timeout=120)
            if run.returncode or run.stdout.strip()!='true':
                (ROOT/'.tools/compound-compiler-failure.watsup').write_text(script.read_text());raise AssertionError((run.returncode,run.stdout,run.stderr))
    finally:f.close();a.close()
    assert before==fingerprint(),'watched inputs changed'
    report={'scope':'original compound prepass barriers, static rejection order, access and compiler ending versus delayed DIM opcode lines; runtime evidence separate','fingerprint':before,'profile':types.PROFILE,'oracle_identity':identity,'source_cases':len(records),'access_sources':len(roles),'access_paths':sum(len(probes) for _,probes in access_cases),'roles':roles,'cases':records,'emission_lines':emissions,'metadata_checks':metadata_checks}
    (ROOT/'coverage/semantics/compound-compiler.json').write_text(json.dumps(report,indent=2)+'\n');print(len(records),'native lint comparisons;',len(roles),'access sources;',report['access_paths'],'access paths;',len(emissions),'emission observations;',len(metadata_checks),'source context boundaries passed')

if __name__=='__main__':main()
