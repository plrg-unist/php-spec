"""Frozen native-first live property-reference graphs in Throwable traces."""

CASES = {
    'one-sided-scalar': br'''<?php
function ex141($x): Exception { return new Exception('same', 7); }
$value = 1; $left = new stdClass; $right = new stdClass; $left->p =& $value; $right->p = 2; $a = ex141($left); $b = ex141($right);
echo 'B|', $a<=>$b, ':', $b<=>$a, '|';
$value = 3; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
$value = 2; echo 'E|', $a<=>$b, ':', (int)($a==$b), '|';
''',
    'paired-alias': br'''<?php
function ex141($x): Exception { return new Exception('same', 7); }
$lv = 1; $rv = 2; $left = new stdClass; $right = new stdClass; $left->p =& $lv; $right->p =& $rv; $a = ex141($left); $b = ex141($right);
echo 'B|', $a<=>$b, '|';
$lv = 3; echo 'L|', $a<=>$b, ':', $b<=>$a, '|';
$rv = 3; echo 'E|', $a<=>$b, '|';
''',
    'array-cell-cow': br'''<?php
function ex141($x): Exception { return new Exception('same', 7); }
$live = [1, 2]; $source = [1, 3]; $left = new stdClass; $right = new stdClass; $left->p =& $live; $right->p = $source; $a = ex141($left); $b = ex141($right);
echo 'B|', $a<=>$b, '|';
$source[1] = 9; $live[1] = 4; echo 'M|', $source[1], ':', $right->p[1], ':', $a<=>$b, ':', $b<=>$a, '|';
$live = [1, 3]; echo 'R|', $a<=>$b, '|';
''',
    'array-count-key': br'''<?php
function ex141($x): Exception { return new Exception('same', 7); }
$v = [1]; $left = new stdClass; $right = new stdClass; $left->p =& $v; $right->p = [1, 2]; $a = ex141($left); $b = ex141($right);
echo 'C|', $a<=>$b, ':', $b<=>$a, '|';
$w = ['x'=>1]; $x = new stdClass; $y = new stdClass; $x->p =& $w; $y->p = ['y'=>1]; $c = ex141($x); $d = ex141($y);
echo 'K|', $c<=>$d, ':', $d<=>$c, '|';
''',
    'object-cell-retarget': br'''<?php
class Plain141 { public int $x = 0; }
function ex141($x): Exception { return new Exception('same', 7); }
$live = new Plain141; $other = new Plain141; $live->x = 1; $other->x = 2; $left = new stdClass; $right = new stdClass; $left->p =& $live; $right->p = $other; $a = ex141($left); $b = ex141($right);
echo 'B|', $a<=>$b, '|';
$live->x = 3; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
$live = new Plain141; $live->x = 2; echo 'R|', $a<=>$b, '|';
''',
    'cell-type-retarget': br'''<?php
function ex141($x): Exception { return new Exception('same', 7); }
$live = 1; $left = new stdClass; $right = new stdClass; $left->p =& $live; $right->p = 1; $a = ex141($left); $b = ex141($right);
echo 'B|', $a<=>$b, '|';
$live = [1, 2]; $right->p = [1, 3]; echo 'A|', $a<=>$b, ':', $b<=>$a, '|';
$live[1] = 4; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'property-array-cell': br'''<?php
function ex141($x): Exception { return new Exception('same', 7); }
$live = 1; $left = new stdClass; $right = new stdClass; $left->payload = [&$live, 9]; $right->payload = [2, 9]; $a = ex141($left); $b = ex141($right);
echo 'B|', $a<=>$b, '|';
$live = 3; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'shared-cell-dag': br'''<?php
function ex141($x): Exception { return new Exception('same', 7); }
$live = 1; $left = new stdClass; $right = new stdClass; $left->first =& $live; $left->second =& $live; $right->first = 1; $right->second = 1; $a = ex141($left); $b = ex141($right);
echo 'B|', $a<=>$b, '|';
$live = 2; echo 'M|', $a<=>$b, '|';
''',
    'seven-operators': br'''<?php
function ex141($x): Exception { return new Exception('same', 7); }
$live = 1; $left = new stdClass; $right = new stdClass; $left->p =& $live; $right->p = 2; $a = ex141($left); $b = ex141($right);
echo 'B|', (int)($a==$b), (int)($a!=$b), (int)($a<$b), (int)($a<=$b), (int)($a>$b), (int)($a>=$b), ':', $a<=>$b, '|';
$live = 2; echo 'E|', (int)($a==$b), (int)($a!=$b), (int)($a<$b), (int)($a<=$b), (int)($a>$b), (int)($a>=$b), ':', $a<=>$b, '|';
''',
    'error-second-argument': br'''<?php
function err141($tag, $x): Error { return new Error('same', 7); }
$live = 1; $left = new stdClass; $right = new stdClass; $left->p =& $live; $right->p = 2; $a = err141(17, $left); $b = err141(17, $right);
echo 'B|', $a<=>$b, '|';
$live = 3; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'aggregate-tail': br'''<?php
class Tail141 { public function __toString(): string { echo 'CAST|'; return 'x'; } }
function ex141($x): Exception { return new Exception('same', 7); }
$live = 1; $left = new stdClass; $right = new stdClass; $left->p =& $live; $right->p = 1; $a = ex141($left); $b = ex141($right); $tail = new Tail141;
echo 'E|', [$a, $tail]<=>[$b, 'x'], '|';
$live = 2; echo 'N|', [$a, $tail]<=>[$b, 'x'], '|';
''',
    'different-class-control': br'''<?php
class Left141 { public int $x = 1; }
class Right141 { public int $x = 1; }
function ex141($x): Exception { return new Exception('same', 7); }
$live = new Left141; $left = new stdClass; $right = new stdClass; $left->p =& $live; $right->p = new Right141; $a = ex141($left); $b = ex141($right);
echo 'B|', $a<=>$b, '|';
''',
    'object-scalar-control': br'''<?php
function ex141($x): Exception { return new Exception('same', 7); }
$live = new stdClass; $live->x = 1; $left = new stdClass; $right = new stdClass; $left->p =& $live; $right->p = 1; $a = ex141($left); $b = ex141($right);
echo 'B|', $a<=>$b, '|';
''',
    'cell-cycle-control': br'''<?php
function ex141($x): Exception { return new Exception('same', 7); }
$left = new stdClass; $right = new stdClass; $lv = $left; $rv = $right; $left->p =& $lv; $right->p =& $rv; $a = ex141($left); $b = ex141($right);
echo 'B|'; try { echo $a<=>$b, '|'; } catch (Error $error) { echo 'E|', $error->getMessage(), '|'; }
''',
}
