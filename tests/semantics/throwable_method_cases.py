"""Frozen initialized public-layout comparisons with uncalled ordinary methods."""

CASES = {
    'method-fields-before-severity': br'''<?php
class Packet155 { public $data; public function unused() { echo 'BAD|'; return 0; } public function __get($name) { echo 'BAD|'; return 0; } }
function outer155($x): ErrorException { global $severity155; return new ErrorException('outer', 7, $severity155, __FILE__, 20); }
$source = [1]; $left = new Packet155; $right = new Packet155; $left->data = $source; $right->data = [2];
$severity155 = 9; $a = outer155($left); $severity155 = 1; $b = outer155($right);
echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';
$source[0] = 99; echo 'C|', $source[0], ':', $left->data[0], ':', $a <=> $b, '|';
$left->data[0] = 3; echo 'M|', $a <=> $b, ':', $b <=> $a, '|';
$left->data[0] = 2; echo 'E|', $a <=> $b, '|';
''',
    'nested-method-alias-tables': br'''<?php
class Packet155 { public $data; public function unused() { echo 'BAD|'; return 0; } }
function child155($x): Exception { return new Exception('inner', 7); }
function outer155($x): TypeError { return new TypeError('outer', 7); }
$live = [1]; $snapshot = $live; $left = new Packet155; $right = new Packet155; $left->data =& $live; $right->data = [2];
$p = child155($left); $q = child155($right); $a = outer155($p); $b = outer155($q);
echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
$live = [3]; $snapshot[0] = 99; echo 'M|', $a <=> $b, ':', $snapshot[0], ':', $left->data[0], '|';
$live = [2]; $sa = (string)$a; $sb = (string)$b; echo 'E|', (int)($sa === $sb), ':', $a <=> $b, '|';
$viewLeft = (array)$left; $viewRight = (array)$right; echo 'T|', $a <=> $b, '|';
$live = [4]; echo 'R|', $viewLeft['data'][0], ':', $viewRight['data'][0], ':', $a <=> $b, '|';
''',
    'method-cycle-before-earlier-field': br'''<?php
class Loop155 { public $value = 0; public $next; public function unused() { echo 'BAD|'; return 0; } public function __isset($name) { echo 'BAD|'; return false; } }
function outer155($x): Error { return new Error('outer', 7); }
$left = new Loop155; $right = new Loop155; $tail = new Loop155; $tail->value = 1; $left->next = $left; $right->next = $tail; $tail->next = null;
$a = outer155($left); $b = outer155($right); $hold = 'hold'; echo 'B|'; $site = __LINE__ + 1;
try { try { $hold = $a <=> $b; echo 'BAD|'; } finally { echo 'F|', $hold, '|'; } }
catch (Error $e) { echo get_class($e), ':', $e->getMessage(), ':', (int)($e->getFile() === __FILE__), ':', (int)($e->getLine() === $site), ':', (int)($e->getTrace() === []), '|'; }
$right->next = $left; echo 'I|', $a <=> $b, ':', (int)($a == $b), '|';
$right->value = 1; echo 'M|', $a <=> $b, ':', $b <=> $a, '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';
''',
    'method-table-count-key-tail': br'''<?php
class Packet155 { public $data; public function unused() { echo 'BAD|'; return 0; } }
class Tail155 { public function __toString() { echo 'BAD|'; return 'x'; } }
function outer155($x): Exception { return new Exception('outer', 7); }
$left = new Packet155; $right = new Packet155; $left->data = ['cycle' => $left, 'extra' => 0]; $right->data = ['cycle' => $right];
$a = outer155($left); $b = outer155($right); echo 'C|', $a <=> $b, ':', $b <=> $a, '|';
$viewLeft = (array)$left; $viewRight = (array)$right; $right->data = ['other' => $right, 'extra' => 0];
echo 'K|', $a <=> $b, ':', $b <=> $a, '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|A|', [0, $a, new Tail155] <=> [0, $b, 'x'], '|';
$left->data = ['x' => [1]]; $right->data = ['x' => [1]]; echo 'E|', $a <=> $b, ':', [0, $a, 1] <=> [0, $b, 3], '|';
''',
    'implicit-stringable-control': br'''<?php
class Stringable155 { public $value = 0; public function __toString(): string { echo 'BAD|'; return 'x'; } }
function outer155($x): Exception { return new Exception('outer', 7); }
$left = new Stringable155; $right = new Stringable155; $left->value = 1; $right->value = 2;
$a = outer155($left); $b = outer155($right); echo 'B|', $a <=> $b, '|';
''',
    'private-layout-control': br'''<?php
class Private155 { private $value = 0; public function __construct($value) { $this->value = $value; } public function unused() { echo 'BAD|'; } }
function outer155($x): Exception { return new Exception('outer', 7); }
$left = new Private155(1); $right = new Private155(2); $a = outer155($left); $b = outer155($right);
echo 'B|', $a <=> $b, '|';
''',
}
