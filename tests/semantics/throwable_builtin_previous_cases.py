"""Frozen native-first same-kind builtin Throwable previous-chain comparisons."""

CASES = {
    'previous-before-severity': br'''<?php
$p9 = new TypeError('inner', 9); $p1 = new TypeError('inner', 1);
$a = new ErrorException('same', 7, 3, 'f.php', 9, $p9); $b = new ErrorException('same', 7, 4, 'f.php', 9, $p1);
echo 'B|', $a<=>$b, ':', $b<=>$a, '|';
$sa = $a->__toString(); $sb = $b->__toString();
echo 'W|', (int)($sa===$sb), ':', $a<=>$b, ':', $b<=>$a, '|';
''',
    'severity-after-equal-previous': br'''<?php
class Tail145 { public function __toString(): string { echo 'BAD|'; return 'x'; } }
$p = new TypeError('inner', 9); $q = new TypeError('inner', 9); $r = new TypeError('inner', 9);
$a = new ErrorException('same', 7, 3, 'f.php', 9, $p); $b = new ErrorException('same', 7, 4, 'f.php', 9, $q); $c = new ErrorException('same', 7, 3, 'f.php', 9, $r);
echo 'B|', $a<=>$b, ':', $b<=>$a, ':', $a<=>$c, '|';
$sa = $a->__toString(); $sb = $b->__toString(); $sc = $c->__toString();
echo 'W|', (int)($sa===$sb), ':', (int)($sa===$sc), ':', $a<=>$b, ':', $a<=>$c, '|';
echo 'A|', [0,$a,1]<=>[0,$c,3], ':', [0,$a,new Tail145]<=>[0,$b,'x'], '|';
''',
    'null-versus-previous': br'''<?php
$p = new ValueError('inner', 1);
$a = new RuntimeException('same', 7); $b = new RuntimeException('same', 7, $p);
echo 'B|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'mixed-previous-kinds': br'''<?php
$p = new TypeError('inner', 1); $q = new ValueError('inner', 1);
$a = new RuntimeException('same', 7, $p); $b = new RuntimeException('same', 7, $q);
echo 'B|', (int)($a==$b), (int)($a!=$b), (int)($a<$b), (int)($a<=$b), (int)($a>$b), (int)($a>=$b), ':', $a<=>$b, ':', $b<=>$a, '|';
''',
    'previous-trace-array': br'''<?php
function child145($x): TypeError { return new TypeError('inner', 7); }
$p = child145([1]); $q = child145([2]);
$a = new RuntimeException('same', 7, $p); $b = new RuntimeException('same', 7, $q);
echo 'B|', $a<=>$b, ':', $b<=>$a, '|';
$sa = $a->__toString(); $sb = $b->__toString();
echo 'W|', (int)($sa===$sb), ':', $a<=>$b, ':', $b<=>$a, '|';
''',
    'depth-three-continuation': br'''<?php
$deep1 = new DivisionByZeroError('deep', 1); $deep2 = new DivisionByZeroError('deep', 1); $deep3 = new DivisionByZeroError('deep', 2);
$mid1 = new ArithmeticError('mid', 2, $deep1); $mid2 = new ArithmeticError('mid', 2, $deep2); $mid3 = new ArithmeticError('mid', 2, $deep3);
$a = new TypeError('root', 3, $mid1); $b = new TypeError('root', 3, $mid2); $c = new TypeError('root', 3, $mid3);
echo 'B|', $a<=>$b, ':', $a<=>$c, ':', $c<=>$a, '|';
echo 'A|', [0,$a,1]<=>[0,$b,3], '|';
''',
    'previous-object-trace-control': br'''<?php
function object_child145($x): TypeError { return new TypeError('inner', 7); }
$p = object_child145(new stdClass); $q = object_child145(new stdClass);
$a = new RuntimeException('same', 7, $p); $b = new RuntimeException('same', 7, $q);
echo 'B|', $a<=>$b, '|';
''',
    'previous-alias-trace-control': br'''<?php
function alias_child145($x): TypeError { return new TypeError('inner', 7); }
$v = 1; $p = alias_child145([&$v]); $q = alias_child145([1]);
$a = new RuntimeException('same', 7, $p); $b = new RuntimeException('same', 7, $q);
echo 'B|', $a<=>$b, '|';
''',
    'old-exception-previous-control': br'''<?php
$p = new Exception('inner', 1); $q = new Exception('inner', 1);
$a = new Exception('same', 7, $p); $b = new Exception('same', 7, $q);
echo 'B|', $a<=>$b, '|';
''',
    'old-typeerror-null-control': br'''<?php
$a = new TypeError('same', 7); $b = new TypeError('same', 7);
echo 'B|', $a<=>$b, '|';
''',
}
