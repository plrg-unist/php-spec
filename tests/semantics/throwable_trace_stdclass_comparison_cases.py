"""Builtin Throwable trace comparisons through live stdClass property tables."""

CASES = {
    'aggregate-tail': br'''<?php
class Tail138 { public function __toString(): string { echo 'CAST|'; return 'x'; } }
function ex138($x): Exception { return new Exception('same', 7); }
$left = new stdClass; $right = new stdClass; $left->x = 1; $right->x = 2; $a = ex138($left); $b = ex138($right); $tail = new Tail138;
$left->x = 2; echo 'E:', [$a, $tail]<=>[$b, 'x'], '|';
$left->x = 4; echo 'N:', [$a, $tail]<=>[$b, 'x'], '|';
''',
    'alias-property-control': br'''<?php
function ex138($x): Exception { return new Exception('same', 7); }
$v = 1; $left = new stdClass; $right = new stdClass; $left->x = &$v; $right->x = 1; $a = ex138($left); $b = ex138($right);
echo 'B|', $a<=>$b, '|';
''',
    'array-property-cow': br'''<?php
function ex138($x): Exception { return new Exception('same', 7); }
$source = [1, 2]; $left = new stdClass; $right = new stdClass; $left->p = $source; $right->p = [1, 3]; $a = ex138($left); $b = ex138($right);
echo 'B|', $a<=>$b, '|';
$source[1] = 9; echo 'S|', $source[1], ':', $left->p[1], ':', $a<=>$b, '|';
$left->p[1] = 4; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'count-and-keys': br'''<?php
function ex138($x): Exception { return new Exception('same', 7); }
$left = new stdClass; $right = new stdClass; $left->a = 1; $right->a = 1; $right->b = 2; $a = ex138($left); $b = ex138($right);
echo 'C|', $a<=>$b, ':', $b<=>$a, '|';
$x = new stdClass; $y = new stdClass; $x->a = 1; $y->b = 1; $c = ex138($x); $d = ex138($y);
echo 'K|', $c<=>$d, ':', $d<=>$c, '|';
''',
    'error-properties': br'''<?php
function err138($x): Error { return new Error('same', 7); }
$left = new stdClass; $right = new stdClass; $left->x = 1; $right->x = 2; $a = err138($left); $b = err138($right);
$left->x = 2; echo 'B|', $a<=>$b, '|';
$left->x = 4; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'live-properties': br'''<?php
function ex138($x): Exception { return new Exception('same', 7); }
$left = new stdClass; $right = new stdClass; $left->x = 1; $right->x = 2; $a = ex138($left); $b = ex138($right);
echo 'B|', $a<=>$b, '|';
$left->x = 3; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
$right->x = 3; echo 'E|', $a<=>$b, '|';
''',
    'nested-object-arg': br'''<?php
function ex138($x): Exception { return new Exception('same', 7); }
$left = new stdClass; $right = new stdClass; $left->x = 1; $right->x = 2; $a = ex138([0, $left]); $b = ex138([0, $right]);
echo 'B|', $a<=>$b, '|';
$left->x = 3; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'object-property-control': br'''<?php
function ex138($x): Exception { return new Exception('same', 7); }
$child = new stdClass; $left = new stdClass; $right = new stdClass; $left->x = $child; $right->x = $child; $a = ex138($left); $b = ex138($right);
echo 'B|', $a<=>$b, '|';
''',
    'object-scalar-control': br'''<?php
function ex138($x): Exception { return new Exception('same', 7); }
$object = new stdClass; $object->x = 1; $a = ex138($object); $b = ex138(1);
echo 'B|', $a<=>$b, '|';
''',
    'second-argument': br'''<?php
function ex138($first, $second): Exception { return new Exception('same', 7); }
$left = new stdClass; $right = new stdClass; $left->x = 1; $right->x = 2; $a = ex138(17, $left); $b = ex138(17, $right);
echo 'B|', $a<=>$b, '|';
$left->x = 3; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'seven-operators': br'''<?php
function ex138($x): Exception { return new Exception('same', 7); }
$left = new stdClass; $right = new stdClass; $left->x = 1; $right->x = 2; $a = ex138($left); $b = ex138($right);
$left->x = 2; echo 'E|', (int)($a==$b), (int)($a!=$b), (int)($a<$b), (int)($a<=$b), (int)($a>$b), (int)($a>=$b), ':', $a<=>$b, '|';
$left->x = 3; echo 'G|', (int)($a==$b), (int)($a!=$b), (int)($a<$b), (int)($a<=$b), (int)($a>$b), (int)($a>=$b), ':', $a<=>$b, '|';
''',
    'shared-identity': br'''<?php
function ex138($x): Exception { return new Exception('same', 7); }
$object = new stdClass; $object->x = 1; $a = ex138($object); $b = ex138($object);
$object->x = 9; echo 'B|', $a<=>$b, '|';
''',
}
