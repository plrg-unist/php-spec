"""Builtin Throwable trace comparisons through live array-valued reference cells."""

CASES = {
    'live-array-and-cow': br'''<?php
function ex137($x): Exception { return new Exception('same', 7); }
$v = [1, 2]; $input = [&$v, 4]; $a = ex137($input); $b = ex137([[1, 3], 4]);
echo 'B|', $a<=>$b, '|';
$v = [1, 3]; $input[1] = 9; echo 'M|', $v[1], ':', $input[1], ':', $a<=>$b, '|';
$v[1] = 5; echo 'R|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'nested-array-cell': br'''<?php
function ex137($x): Exception { return new Exception('same', 7); }
$v = ['x' => [1, 2]]; $a = ex137([&$v]); $b = ex137([['x' => [1, 3]]]);
echo 'B|', $a<=>$b, '|';
$v['x'][1] = 3; echo 'M|', $a<=>$b, '|';
$v['x'][1] = 4; echo 'R|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'count-and-keys': br'''<?php
function ex137($x): Exception { return new Exception('same', 7); }
$v = [1]; $a = ex137([&$v]); $b = ex137([[1, 2]]); $c = ex137([[0 => 1]]);
echo 'C|', $a<=>$b, ':', $b<=>$a, '|';
$v = [1 => 1]; echo 'K|', $a<=>$c, ':', $c<=>$a, '|';
''',
    'shared-child-array-cell': br'''<?php
function ex137($x): Exception { return new Exception('same', 7); }
$v = [1]; $child = [&$v]; $left = [$child, $child]; $right = [$child, $child]; $a = ex137($left); $b = ex137($right);
$v = [3]; echo 'B|', $a<=>$b, '|';
''',
    'error-array-cell': br'''<?php
function err137($x): Error { return new Error('same', 7); }
$v = [1]; $a = err137([&$v]); $b = err137([[2]]);
$v = [2]; echo 'B|', $a<=>$b, '|';
$v = [4]; echo 'R|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'aggregate-tail': br'''<?php
class Tail137 { public function __toString(): string { echo 'CAST|'; return 'x'; } }
function ex137($x): Exception { return new Exception('same', 7); }
$v = [1]; $a = ex137([&$v]); $b = ex137([[2]]); $c = ex137([[3]]); $tail = new Tail137;
$v = [2]; echo 'E:', [$a, $tail]<=>[$b, 'x'], '|';
$v = [4]; echo 'N:', [$a, $tail]<=>[$c, 'x'], '|';
''',
    'seven-operators': br'''<?php
function ex137($x): Exception { return new Exception('same', 7); }
$v = [1]; $a = ex137([&$v]); $b = ex137([[2]]);
$v = [2]; echo 'E|', (int)($a==$b), (int)($a!=$b), (int)($a<$b), (int)($a<=$b), (int)($a>$b), (int)($a>=$b), ':', $a<=>$b, '|';
$v = [3]; echo 'G|', (int)($a==$b), (int)($a!=$b), (int)($a<$b), (int)($a<=$b), (int)($a>$b), (int)($a>=$b), ':', $a<=>$b, '|';
''',
    'object-cell-control': br'''<?php
function ex137($x): Exception { return new Exception('same', 7); }
$v = [new stdClass]; $a = ex137([&$v]); $b = ex137([&$v]);
echo 'B|', $a<=>$b, '|';
''',
    'cycle-cell-control': br'''<?php
function ex137($x): Exception { return new Exception('same', 7); }
$v = []; $v[0] = &$v; $a = ex137([&$v]); $b = ex137([&$v]);
echo 'B|', $a<=>$b, '|';
''',
    'primitive-cell-control': br'''<?php
function ex137($x): Exception { return new Exception('same', 7); }
$v = 1; $a = ex137([&$v]); $b = ex137([2]);
echo 'B|', $a<=>$b, '|';
''',
}
