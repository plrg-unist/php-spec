#!/usr/bin/env python3
"""Reference returns preserve source designation, alias coercion and result owners."""
from pathlib import Path
import function_scope as scope

CASES = {'ref-return-bare': b'<?php function &f(){return;} $x=&f();echo $x===null;',
 'ref-return-implicit': b'<?php function &f(){} $x=&f();echo $x===null;',
 'ref-return-unused-constant': b'<?php function &f(){return 1;}f();echo "E";',
 'ref-return-unused-local': b'<?php function &f(){$x=1;return $x;}f();echo "E";',
 'ref-return-forward-reference': b'<?php $x=1;function &g(){global $x;return $x;}function &f(){retu'
                                 b'rn g();}$r=&f();$r=2;echo $x;',
 'ref-return-forward-value': b'<?php function g(){return 1;}function &f(){return g();}$r=&f();echo '
                             b'$r;',
 'ref-return-forward-unused': b'<?php function g(){return 1;}function &f(){return g();}f();echo '
                              b'"E";',
 'ref-return-typed-alias-coercion': b'<?php $x="2";$alias=&$x;function &f():int{global $x;return $'
                                    b'x;}$r=&f();echo $x===2,$alias===2;$r=3;echo $x,$alias;',
 'ref-return-void-bare': b'<?php function &f():void{return;}f();echo "E";',
 'return-ref-computed-missing': b'<?php function &f(){$n="x";return $$n;}$x=&f();$x=3;echo $x;',
 'return-ref-computed-typed-alias': b'<?php $x="1";$a=&$x;function &f():int{global $x;$n="x";retur'
                                    b'n $$n;}$r=&f();echo $x===1,$a===1;$r=3;echo $x,$a;',
 'return-ref-nested-leaf-cow': b'<?php $a=[[1]];$b=$a;function &f(){global $a;return $a[0][0];}$x'
                               b'=&f();$x=3;echo $a[0][0],$b[0][0];',
 'return-ref-temporary-call-leaf': b'<?php function g(){return [1];}function &f(){return g()[0];}'
                                   b'$x=&f();$x=3;echo $x;',
 'return-ref-nullable-missing': b'<?php function &f():?int{return $x;}$x=&f();echo $x===null;$x=3;'
                                b'echo $x;',
 'return-ref-nullable-unused': b'<?php function &f():?int{return $x;}f();echo 1;',
 'return-ref-typed-call-shared': b'<?php $x="1";$a=&$x;function &g(){global $x;return $x;}function '
                                 b'&f():int{return g();}$r=&f();echo $a===1,$x===1;$r=3;echo $a,$x;',
 'return-ref-string-offset-error': b'<?php $s="abc";function &f(){global $s;return $s[0];}$x=&f()'
                                   b';echo $x;',
 'return-reference-assignment-value-class': b'<?php $x=1;$y=2;function &f(){global $x,$y;return ($'
                                            b'x=&$y);}$r=&f();$r=3;echo $x,$y;',
 'return-whole-globals-copy': b'<?php $x=1;function &f(){return $GLOBALS;}$r=&f();$r["x"]=2;echo'
                              b' $x,$r["x"];',
 'param-byref-call-value': b'<?php function g(){return 1;} function f(&$x){echo "body",$x;} f(g()'
                           b');',
 'param-byref-call-reference': b'<?php $a=1;function &g(){global $a;return $a;}function f(&$x){$x'
                               b'=3;}f(g());echo $a;',
 'return-ref-missing': b'<?php function &f(){return $x;} $a=&f();$a=2;echo $a;',
 'return-ref-temporary': b'<?php function &f(){return 1;} $a=&f();echo $a;',
 'return-ref-value-consumer': b'<?php $x=1;function &f(){global $x;return $x;} $a=f();$a=3;echo '
                              b'$x,$a;',
 'byref-return-compile-read': b'<?php function &f(){return $a[];} $x=&f();$x=3;echo $x;',
 'byref-return-nullsafe': b'<?php function &f(){return $a?->x;}',
 'ref-bare-multiline': b'<?php\nfunction &f()\n{\n return;\n}\nf();',
 'ref-implicit-multiline': b'<?php\nfunction &f()\n{\n $x=1;\n}\nf();',
 'ref-return-call-argument-line': b'<?php\nfunction g($x){return [];}\nfunction &f():int {\n return'
                                  b' g(\n 1\n );\n}\nf();',
 'ref-return-nested-call-line': b'<?php\nfunction g($x){return [];}\nfunction h($x){return $x;}\n'
                                b'function &f():int {\n return g(\n h(\n  1\n )\n );\n}\nf();',
 'ref-return-nullary-call-line': b'<?php\nfunction g(){return [];}\nfunction &f():int {\n return\n '
                                 b'g();\n}\nf();'}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'reference-returns', Path(__file__)) else 1)
