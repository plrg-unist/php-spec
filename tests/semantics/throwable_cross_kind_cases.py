"""Frozen native-first exact builtin Exception/Error class-mismatch comparisons."""

CASES = {
    'seven-operators': br'''<?php
$a = new Exception('same', 7); $b = new Error('same', 7);
echo 'B|', (int)($a==$b), (int)($a!=$b), (int)($a<$b), (int)($a<=$b), (int)($a>$b), (int)($a>=$b), ':', $a<=>$b, ':', $b<=>$a, '|';
echo 'S|', (int)($a===$b), ':', (int)($a!==$b), '|';
''',
    'warm-live-trace': br'''<?php
function ex142($x): Exception { return new Exception('same', 7); }
function er142($x): Error { return new Error('same', 7); }
$arg = new stdClass; $arg->v = 1; $a = ex142($arg); $b = er142($arg);
echo 'C|', $a<=>$b, ':', $b<=>$a, '|';
$a->__toString(); echo 'L|', $a<=>$b, ':', $b<=>$a, '|';
$b->__toString(); echo 'W|', $a<=>$b, ':', $b<=>$a, '|';
$arg->v = 9; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'previous-links': br'''<?php
$p = new Exception('inner', 1); $q = new Error('inner', 2); $a = new Exception('same', 7, $p); $b = new Error('same', 7, $q);
echo 'B|', $a<=>$b, ':', $b<=>$a, ':', (int)($a==$b), '|';
$a->__toString(); $b->__toString(); echo 'W|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'cyclic-trace-skip': br'''<?php
class Bomb142 { public function __toString(): string { echo 'BAD|'; throw new Exception('caster reached'); } }
function ex142($x): Exception { return new Exception('same', 7); }
function er142($x): Error { return new Error('same', 7); }
$left = new stdClass; $right = new stdClass; $left->self = $left; $right->self = $right; $a = ex142([$left, new Bomb142]); $b = er142([$right, new Bomb142]);
echo 'B|', $a<=>$b, ':', $b<=>$a, '|';
$left->extra = 9; $right->extra = 10; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'state-skip': br'''<?php
class Tail142 { public function __toString(): string { echo 'BAD|'; return 'x'; } }
function ex142($x): Exception { return new Exception('same', 7); }
function er142($x): Error { return new Error('same', 7); }
$left = new stdClass; $right = new stdClass; $left->self = $left; $right->self = $right; $a = ex142($left); $b = er142($right); $tail = new Tail142;
echo 'B|', $a<=>$b, '|';
echo 'A|', [0,$a,$tail]<=>[0,$b,'x'], '|';
''',
    'same-kind-cold-control': br'''<?php
$a = new Exception('same', 7); $b = new Exception('same', 7);
echo 'B|', $a<=>$b, ':', (int)($a==$b), ':', (int)($a===$b), '|';
''',
    'same-kind-cycle-control': br'''<?php
function ex142($x): Exception { return new Exception('same', 7); }
$left = new stdClass; $right = new stdClass; $left->self = $left; $right->self = $right; $a = ex142($left); $b = ex142($right);
echo 'B|'; try { echo $a<=>$b, '|'; } catch (Error $error) { echo 'E|', $error->getMessage(), '|'; }
''',
}
