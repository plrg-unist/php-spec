"""Builtin Throwable trace comparisons through live nested reference cells."""

CASES = {
    'live-cell-and-copy': br'''<?php
function ex136($x): Exception { return new Exception('same', 7); }
$v = 1; $alias = [&$v]; $plain = [1]; $a = ex136($alias); $b = ex136([2]); $c = ex136($plain);
echo 'B|', $a<=>$b, ':', $c<=>$b, '|';
$v = 2; $plain[0] = 9; echo 'M|', $alias[0], ':', $plain[0], ':', $a<=>$b, ':', $c<=>$b, '|';
$v = 3; echo 'R|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'alias-and-cow-sibling': br'''<?php
function ex136($x): Exception { return new Exception('same', 7); }
$v = 1; $source = [&$v, 1]; $a = ex136($source); $b = ex136([2, 1]);
echo 'B|', $a<=>$b, '|';
$v = 2; $source[1] = 9; echo 'M|', $source[0], ':', $source[1], ':', $a<=>$b, '|';
$v = 3; echo 'R|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'nested-alias': br'''<?php
function ex136($x): Exception { return new Exception('same', 7); }
$v = 1; $left = ['x'=>[&$v, 4]]; $a = ex136($left); $b = ex136(['x'=>[2, 4]]);
echo 'B|', $a<=>$b, '|';
$v = 2; echo 'M|', $a<=>$b, '|';
$v = 3; echo 'R|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'count-and-keys': br'''<?php
function ex136($x): Exception { return new Exception('same', 7); }
$v = 1; $a = ex136([&$v]); $b = ex136([1, 2]); $c = ex136([1=>&$v]); $d = ex136([0=>&$v]);
echo 'B|', $a<=>$b, ':', $b<=>$a, '|', $c<=>$d, ':', $d<=>$c, '|';
''',
    'shared-child-cell': br'''<?php
function ex136($x): Exception { return new Exception('same', 7); }
$v = 1; $child = [&$v]; $left = [$child, $child]; $right = [$child, $child]; $a = ex136($left); $b = ex136($right);
$v = 3; echo 'B|', $a<=>$b, '|';
''',
    'error-live-cell': br'''<?php
function err136($x): Error { return new Error('same', 7); }
$v = 1; $a = err136([&$v]); $b = err136([2]);
$v = 2; echo 'B|', $a<=>$b, '|';
$v = 4; echo 'R|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'aggregate-tail': br'''<?php
class Tail136 { public function __toString(): string { echo 'CAST|'; return 'x'; } }
function ex136($x): Exception { return new Exception('same', 7); }
$v = 1; $a = ex136([&$v]); $b = ex136([2]); $c = ex136([3]); $tail = new Tail136;
$v = 2; echo 'E:', [$a,$tail]<=>[$b,'x'], '|';
$v = 4; echo 'N:', [$a,$tail]<=>[$c,'x'], '|';
''',
    'object-cell-control': br'''<?php
function ex136($x): Exception { return new Exception('same', 7); }
$v = new stdClass; $a = ex136([&$v]); $b = ex136([&$v]);
echo 'B|', $a<=>$b, '|';
''',
    'array-cell-control': br'''<?php
function ex136($x): Exception { return new Exception('same', 7); }
$v = [1]; $a = ex136([&$v]); $b = ex136([[1]]);
echo 'B|', $a<=>$b, '|';
''',
    'direct-control': br'''<?php
function ex136($x): Exception { return new Exception('same', 7); }
$a = ex136([1]); $b = ex136([2]);
echo 'B|', $a<=>$b, '|';
''',
}
