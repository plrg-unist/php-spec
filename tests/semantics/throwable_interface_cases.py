"""Frozen ordinary interface images; trap methods are never comparison callbacks."""

CASES = {
    'stringable-fields-before-severity': br'''<?php
class Packet156 { public $data; public function __toString(): string { echo 'BAD|'; return 'x'; } }
function outer156($x): ErrorException { global $severity156; return new ErrorException('outer', 7, $severity156, __FILE__, 20); }
$source = [1]; $left = new Packet156; $right = new Packet156; $left->data = $source; $right->data = [2];
$severity156 = 9; $a = outer156($left); $severity156 = 1; $b = outer156($right);
echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';
$source[0] = 99; echo 'C|', $source[0], ':', $left->data[0], ':', $a <=> $b, '|';
$left->data[0] = 3; echo 'M|', $a <=> $b, ':', $b <=> $a, '|';
$left->data[0] = 2; echo 'E|', $a <=> $b, '|';
''',
    'source-interface-alias-tables': br'''<?php
interface Tag156 { public function ping(); }
class Packet156 implements Tag156 { public $data; public function ping() { echo 'BAD|'; return 0; } }
function child156($x): Exception { return new Exception('inner', 7); }
function outer156($x): TypeError { return new TypeError('outer', 7); }
$live = [1]; $snapshot = $live; $left = new Packet156; $right = new Packet156; $left->data =& $live; $right->data = [2];
$p = child156($left); $q = child156($right); $a = outer156($p); $b = outer156($q);
echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
$live = [3]; $snapshot[0] = 99; echo 'M|', $a <=> $b, ':', $snapshot[0], ':', $left->data[0], '|';
$live = [2]; $sa = (string)$a; $sb = (string)$b; echo 'E|', (int)($sa === $sb), ':', $a <=> $b, '|';
foreach ($left as $ignored) {} foreach ($right as $ignored) {}
$viewLeft = (array)$left; $viewRight = (array)$right; echo 'T|', $a <=> $b, '|';
$live = [4]; echo 'R|', $viewLeft['data'][0], ':', $viewRight['data'][0], ':', $a <=> $b, '|';
''',
    'stringable-cycle-no-cast': br'''<?php
class Loop156 { public $value = 0; public $next = null; public function __toString(): string { echo 'BAD|'; return 'x'; } }
function outer156($x): Error { return new Error('outer', 7); }
$left = new Loop156; $right = new Loop156; $left->value = 1; $right->value = 2; $left->next = $left; $right->next = $right;
$a = outer156($left); $b = outer156($right); echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';
$left->value = 2; $hold = 'hold'; echo 'C|'; $site = __LINE__ + 1;
try { try { $hold = $a <=> $b; echo 'BAD|'; } finally { echo 'F|', $hold, '|'; } }
catch (Error $e) { echo get_class($e), ':', $e->getMessage(), ':', (int)($e->getFile() === __FILE__), ':', (int)($e->getLine() === $site), ':', (int)($e->getTrace() === []), '|'; }
$right->next = $left; echo 'I|', $a <=> $b, ':', (int)($a == $b), '|';
$left->value = 1; echo 'R|', $a <=> $b, ':', $b <=> $a, '|';
''',
    'interface-count-key-class-skips': br'''<?php
interface Marker156 {}
class Packet156 implements Marker156 { public $data; public function unused() { echo 'BAD|'; return 0; } }
class Other156 implements Marker156 { private $value = 0; public function __construct($value) { $this->value = $value; } }
class Tail156 { public function __toString() { echo 'BAD|'; return 'x'; } }
function outer156($x): Exception { return new Exception('outer', 7); }
$left = new Packet156; $right = new Packet156; $left->data = ['cycle' => $left, 'extra' => 0]; $right->data = ['cycle' => $right];
$a = outer156($left); $b = outer156($right); echo 'C|', $a <=> $b, ':', $b <=> $a, '|';
foreach ($left as $ignored) {} foreach ($right as $ignored) {}
$right->data = ['other' => $right, 'extra' => 0]; echo 'K|', $a <=> $b, ':', $b <=> $a, '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|A|', [0, $a, new Tail156] <=> [0, $b, 'x'], '|';
$foreign = new Other156($left); $c = outer156($left); $d = outer156($foreign); echo 'D|', $c <=> $d, ':', $d <=> $c, '|';
$left->data = ['x' => [1]]; $right->data = ['x' => [1]]; echo 'E|', $a <=> $b, ':', [0, $a, 1] <=> [0, $b, 3], '|';
''',
    'stringable-scalar-control': br'''<?php
class Packet156 { public $value = 1; public function __toString(): string { return 'q'; } }
function outer156($x): Exception { return new Exception('outer', 7); }
$left = new Packet156; $a = outer156($left); $b = outer156('z'); echo 'B|', $a <=> $b, '|';
''',
    'inherited-interface-layout-control': br'''<?php
interface Marker156 {}
class Base156 { public $value = 0; }
class Child156 extends Base156 implements Marker156 { public function unused() { echo 'BAD|'; } }
function outer156($x): Exception { return new Exception('outer', 7); }
$left = new Child156; $right = new Child156; $left->value = 1; $right->value = 2;
$a = outer156($left); $b = outer156($right); echo 'B|', $a <=> $b, '|';
''',
}
