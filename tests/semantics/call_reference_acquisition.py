#!/usr/bin/env python3
"""Call reference assignment keeps values distinct from returned alias cells."""
from pathlib import Path
import function_scope as scope

CASES = {
    'call-ref-rebind-target-array': b'<?php $a=[1];$old=&$a[0];function g(){global $a;$a=[2];return 3;}$a[0]=&g();echo $old,$a[0];',
    'call-ref-remove-target-array': b'<?php $a=[1];$old=&$a[0];function g(){global $a;unset($a);return 3;}$a[0]=&g();echo $old,$a[0];',
    'call-ref-delayed-key': b'<?php $a=[1,2];$k=0;function g(){global $k;$k=1;return 3;}$a[$k]=&g();echo $a[0],$a[1];',
    'call-ref-captured-key': b'<?php $a=[1,2];$k=0;function keyf(){global $k;return $k;}function g(){global $k;$k=1;return 3;}$a[keyf()]=&g();echo $a[0],$a[1];',
    'call-ref-computed-name': b'<?php $n="a";$a=1;$b=2;function g(){global $n;$n="b";return 3;}$$n=&g();echo $a,$b;',
    'call-ref-global-slot': b'<?php $x=1;$a=&$x;function g(){return 3;}$GLOBALS["x"]=&g();echo $a,$x;',
    'call-ref-superglobal-slot': b'<?php $_GET=[1];$a=&$_GET;function g(){return [3];}function f(){$_GET=&g();}f();echo $a[0],$_GET[0];',
    'call-ref-string-target-error': b'<?php $s="abc";function g(){echo "G";return 3;}$s[0]=&g();',
    'call-ref-scalar-target-error': b'<?php $a=1;function g(){echo "G";return 3;}$a[0]=&g();',
    'call-ref-key-target-error': b'<?php $a=[];function g(){echo "G";return 3;}$a[[]]=&g();',
    'call-ref-temporary-target-error': b'<?php function a(){return [1];}function g(){echo "G";return 3;}a()[0]=&g();',
    'call-ref-append-returned-array': b'<?php $a=[];function g(){return [2];}$a[]=&g();$b=$a;$a[0][0]=3;echo $a[0][0],$b[0][0];',
    'call-ref-expression-result-alias': b'<?php $x=[1];$y=&$x;function g(){return [2];}$a=[$x=&g()];$x[0]=3;echo $a[0][0],$y[0];',
    'acquire-argument-line-cv': b'<?php\nfunction g($x){return $x;}\n$x=&g(\n 1\n);\necho $x;',
    'acquire-argument-line-computed': b'<?php\nfunction g($x){return $x;}\n$n="x";\n$$n=&g(\n 1\n);\necho $x;',
    'acquire-argument-line-dim': b'<?php\nfunction g($x){return $x;}\n$a=[];\n$a[\n 0\n]=&g(\n 1\n);\necho $a[0];',
    'acquire-argument-line-nested': b'<?php\nfunction g($x){return $x;}\nfunction h($x){return $x;}\n$x=&g(\n h(\n  1\n )\n);\necho $x;',
}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'call-reference-acquisition', Path(__file__)) else 1)
