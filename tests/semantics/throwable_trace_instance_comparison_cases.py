"""Frozen native-first Throwable trace comparisons through ordinary objects."""

CASES = {
    'inline-declared-order': br'''<?php
class Plain139 { public int $first = 0; public int $second = 0; }
function ex139($x): Exception { return new Exception('same', 7); }
$left = new Plain139; $right = new Plain139; $left->first = 1; $right->first = 1; $left->second = 1; $right->second = 2; $a = ex139($left); $b = ex139($right);
echo 'B|', $a<=>$b, '|';
$left->second = 3; echo 'S|', $a<=>$b, ':', $b<=>$a, '|';
$left->first = 0; echo 'F|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'inline-seven-operators': br'''<?php
class Plain139 { public int $first = 0; public int $second = 0; }
function ex139($x): Exception { return new Exception('same', 7); }
$left = new Plain139; $right = new Plain139; $left->first = 1; $right->first = 2; $left->second = 9; $right->second = 0; $a = ex139($left); $b = ex139($right);
echo 'B|', (int)($a==$b), (int)($a!=$b), (int)($a<$b), (int)($a<=$b), (int)($a>$b), (int)($a>=$b), ':', $a<=>$b, '|';
$left->first = 2; $left->second = 0; echo 'E|', (int)($a==$b), (int)($a!=$b), (int)($a<$b), (int)($a<=$b), (int)($a>$b), (int)($a>=$b), ':', $a<=>$b, '|';
''',
    'inline-same-identity': br'''<?php
class Plain139 { public int $first = 1; public int $second = 2; }
function ex139($x): Exception { return new Exception('same', 7); }
$object = new Plain139; $a = ex139($object); $b = ex139($object);
$object->second = 9; echo 'B|', $a<=>$b, '|';
''',
    'inline-array-cow': br'''<?php
class Plain139 { public int $first = 1; public array $second = []; }
function ex139($x): Exception { return new Exception('same', 7); }
$source = [1, 2]; $left = new Plain139; $right = new Plain139; $left->second = $source; $right->second = [1, 3]; $a = ex139($left); $b = ex139($right);
echo 'B|', $a<=>$b, '|';
$source[1] = 9; echo 'C|', $source[1], ':', $left->second[1], ':', $a<=>$b, '|';
$left->second[1] = 4; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'materialized-one-sided': br'''<?php
class Plain139 { public int $first = 1; public int $second = 0; }
function ex139($x): Exception { return new Exception('same', 7); }
$left = new Plain139; $right = new Plain139; $left->second = 1; $right->second = 2; $snapshot = (array)$left; $a = ex139($left); $b = ex139($right);
echo 'B|', $a<=>$b, '|';
$left->second = 3; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'materialized-dynamic-count-key': br'''<?php
#[AllowDynamicProperties]
class Plain139 { public int $base = 1; }
function ex139($x): Exception { return new Exception('same', 7); }
$left = new Plain139; $right = new Plain139; $left->x = 1; $right->x = 1; $right->y = 2; $a = ex139($left); $b = ex139($right);
echo 'C|', $a<=>$b, ':', $b<=>$a, '|';
$x = new Plain139; $y = new Plain139; $x->x = 1; $y->y = 1; $c = ex139($x); $d = ex139($y);
echo 'K|', $c<=>$d, ':', $d<=>$c, '|';
''',
    'materialized-dynamic-live': br'''<?php
#[AllowDynamicProperties]
class Plain139 { public int $base = 1; }
function ex139($x): Exception { return new Exception('same', 7); }
$left = new Plain139; $right = new Plain139; $left->extra = 1; $right->extra = 2; $a = ex139($left); $b = ex139($right);
echo 'B|', $a<=>$b, '|';
$left->extra = 3; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'materialized-dynamic-array-cow': br'''<?php
#[AllowDynamicProperties]
class Plain139 { public int $base = 1; }
function ex139($x): Exception { return new Exception('same', 7); }
$source = [1, 2]; $left = new Plain139; $right = new Plain139; $left->payload = $source; $right->payload = [1, 3]; $a = ex139($left); $b = ex139($right);
echo 'B|', $a<=>$b, '|';
$source[1] = 9; echo 'C|', $source[1], ':', $left->payload[1], ':', $a<=>$b, '|';
$left->payload[1] = 4; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'error-second-argument': br'''<?php
class Plain139 { public int $first = 1; public int $second = 0; }
function err139($tag, $x): Error { return new Error('same', 7); }
$left = new Plain139; $right = new Plain139; $left->second = 1; $right->second = 2; $a = err139(17, $left); $b = err139(17, $right);
echo 'B|', $a<=>$b, '|';
$left->second = 3; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'aggregate-tail': br'''<?php
class Plain139 { public int $first = 1; public int $second = 1; }
class Tail139 { public function __toString(): string { echo 'CAST|'; return 'x'; } }
function ex139($x): Exception { return new Exception('same', 7); }
$left = new Plain139; $right = new Plain139; $a = ex139($left); $b = ex139($right); $tail = new Tail139;
echo 'E|', [$a, $tail]<=>[$b, 'x'], '|';
$left->second = 3; echo 'N|', [$a, $tail]<=>[$b, 'x'], '|';
''',
    'different-class-control': br'''<?php
class Left139 { public int $x = 1; }
class Right139 { public int $x = 1; }
function ex139($x): Exception { return new Exception('same', 7); }
$left = new Left139; $right = new Right139; $a = ex139($left); $b = ex139($right);
echo 'B|', $a<=>$b, '|';
''',
    'object-scalar-control': br'''<?php
class Plain139 { public int $x = 1; }
function ex139($x): Exception { return new Exception('same', 7); }
$object = new Plain139; $a = ex139($object); $b = ex139(1);
echo 'B|', $a<=>$b, '|';
''',
    'hook-property-control': br'''<?php
class Hook139 { public int $x = 1 { get { echo 'G|'; return $this->x; } } }
function ex139($x): Exception { return new Exception('same', 7); }
$left = new Hook139; $right = new Hook139; $a = ex139($left); $b = ex139($right);
echo 'B|', $a<=>$b, '|';
''',
    'alias-property-control': br'''<?php
class Plain139 { public $x = 0; }
function ex139($x): Exception { return new Exception('same', 7); }
$value = 1; $left = new Plain139; $right = new Plain139; $left->x =& $value; $right->x = 1; $a = ex139($left); $b = ex139($right);
echo 'B|', $a<=>$b, '|';
''',
}
