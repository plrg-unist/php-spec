"""Frozen empty effective layouts, honest caches and ordinary dynamic tables."""

CASES = {
    'empty-inline-before-severity': br'''<?php
interface Marker158 {}
class Base158 implements Marker158 { public static $noise = 0; public function unused() { echo 'BAD|'; } }
class Packet158 extends Base158 { public function __toString(): string { echo 'BAD|'; return 'x'; } }
function outer158($x): Exception { return new Exception('outer', 7); }
function severity158($x): ErrorException { global $severity158; return new ErrorException('outer', 7, $severity158, __FILE__, 20); }
$left = new Packet158; $right = new Packet158; $a = outer158($left); $b = outer158($right);
echo 'B|', $a <=> $b, ':', (int)($a == $b), ':', (int)($a != $b), ':', (int)($a < $b), ':', (int)($a <= $b), ':', (int)($a > $b), ':', (int)($a >= $b), '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';
Packet158::$noise = NAN; echo 'N|', $a <=> $b, ':', [0, $a, 1] <=> [0, $b, 3], '|';
$severity158 = 9; $c = severity158($left); $severity158 = 1; $d = severity158($right); echo 'S|', $c <=> $d, ':', $d <=> $c, '|';
''',
    'empty-foreach-cast-caches': br'''<?php
class Packet158 { public function unused() { echo 'BAD|'; } }
function outer158($x): Exception { return new Exception('outer', 7); }
$left = new Packet158; $right = new Packet158; $a = outer158($left); $b = outer158($right);
echo 'B|', $a <=> $b, '|';
$cast = (array)$left; $copy = $cast; $copy['x'] = 1; echo 'A|', (int)($cast === []), ':', $a <=> $b, '|';
foreach ($left as $ignored) {} echo 'L|', $a <=> $b, ':', $b <=> $a, '|';
foreach ($right as $ignored) {} echo 'R|', $a <=> $b, '|';
$viewLeft = (array)$left; $viewRight = (array)$right; $viewLeft['x'] = 1; echo 'V|', (int)($viewRight === []), ':', $viewLeft['x'], ':', $a <=> $b, '|';
''',
    'empty-dynamic-alias-count-cycle': br'''<?php
#[AllowDynamicProperties]
class Packet158 { public function __toString(): string { echo 'BAD|'; return 'x'; } }
function outer158($x): TypeError { return new TypeError('outer', 7); }
$left = new Packet158; $right = new Packet158; $live = [1]; $snapshot = $live; $a = outer158($left); $b = outer158($right);
echo 'B|', $a <=> $b, '|';
$left->data =& $live; echo 'C|', $a <=> $b, ':', $b <=> $a, '|';
$right->data = [2]; echo 'D|', $a <=> $b, ':', $b <=> $a, '|';
$view = (array)$left; $snapshot[0] = 99; $live = [3]; echo 'M|', $view['data'][0], ':', $snapshot[0], ':', $a <=> $b, '|';
$live = [2]; echo 'E|', $a <=> $b, '|';
$cycleLeft = new Packet158; $cycleRight = new Packet158; $cycleLeft->data = ['x' => $cycleLeft]; $cycleRight->data = ['x' => $cycleRight]; $p = outer158($cycleLeft); $q = outer158($cycleRight);
$hold = 'hold'; echo 'X|'; $site = __LINE__ + 1;
try { try { $hold = $p <=> $q; echo 'BAD|'; } finally { echo 'F|', $hold, '|'; } }
catch (Error $e) { echo get_class($e), ':', $e->getMessage(), ':', (int)($e->getFile() === __FILE__), ':', (int)($e->getLine() === $site), ':', (int)($e->getTrace() === []), '|'; }
$countLeft = new Packet158; $countRight = new Packet158; $countLeft->cycle = $countLeft; $countLeft->extra = 0; $countRight->cycle = $countRight; $c = outer158($countLeft); $d = outer158($countRight); echo 'K|', $c <=> $d, ':', $d <=> $c, '|';
$keyLeft = new Packet158; $keyRight = new Packet158; $keyLeft->left = $keyLeft; $keyRight->right = $keyRight; $e = outer158($keyLeft); $f = outer158($keyRight); echo 'Q|', $e <=> $f, ':', $f <=> $e, '|';
''',
    'empty-trace-owned-targets': br'''<?php
class Packet158 { public function unused() { echo 'BAD|'; } }
class Other158 { private $hidden = 0; }
function outer158($x): Exception { return new Exception('outer', 7); }
$left = new Packet158; $right = new Packet158; $weak = WeakReference::create($left); $a = outer158($left); $b = outer158($right);
echo 'B|', $a <=> $b, '|';
$left = null; echo 'H|', (int)($weak->get() !== null), ':', $a <=> $b, '|';
$saved = $a->getTrace(); $a = null; echo 'T|', (int)($weak->get() === $saved[0]['args'][0]), '|';
$saved[0]['args'][0] = null; echo 'D|', (int)($weak->get() === null), '|';
$foreign = new Other158; $c = outer158($right); $d = outer158($foreign); echo 'K|', $c <=> $d, ':', $d <=> $c, '|';
''',
    'empty-dynamic-unset-control': br'''<?php
#[AllowDynamicProperties]
class Packet158 {}
function outer158($x): Exception { return new Exception('outer', 7); }
$left = new Packet158; $right = new Packet158; $left->data = 1; $right->data = 2; unset($left->data, $right->data);
$a = outer158($left); $b = outer158($right); echo 'B|', $a <=> $b, '|';
''',
    'empty-inherited-dynamic-control': br'''<?php
#[AllowDynamicProperties]
class Base158 {}
class Packet158 extends Base158 { public function unused() { echo 'BAD|'; } }
function outer158($x): Exception { return new Exception('outer', 7); }
$left = new Packet158; $right = new Packet158; $left->data = 1; $right->data = 2;
$a = outer158($left); $b = outer158($right); echo 'B|', $a <=> $b, '|';
''',
}
