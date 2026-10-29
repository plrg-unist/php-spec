"""Frozen inherited ordinary images; comparison never invokes trap methods."""

CASES = {
    'inherited-physical-slots-before-severity': br'''<?php
class Base157 { public $first = 0; public $baseTail = 0; public function __get(string $name) { echo 'BAD|'; return null; } }
class Middle157 extends Base157 { public $middle = 0; public $first = 0; }
class Leaf157 extends Middle157 { public $leaf = 0; public function unused() { echo 'BAD|'; } }
function outer157($x): ErrorException { global $severity157; return new ErrorException('outer', 7, $severity157, __FILE__, 20); }
$left = new Leaf157; $right = new Leaf157; $left->first = 1; $right->first = 2; $left->baseTail = 9; $right->baseTail = 1; $left->middle = 9; $right->middle = 1; $left->leaf = 9; $right->leaf = 1;
$severity157 = 9; $a = outer157($left); $severity157 = 1; $b = outer157($right);
echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';
$left->first = 2; echo 'P|', $a <=> $b, '|';
$left->baseTail = 1; $left->middle = 0; echo 'M|', $a <=> $b, '|';
$left->middle = 1; $left->leaf = 0; echo 'L|', $a <=> $b, '|';
$left->leaf = 1; echo 'S|', $a <=> $b, '|';
foreach ($left as $ignored) {} foreach ($right as $ignored) {}
$left->first = 0; echo 'T|', $a <=> $b, ':', $b <=> $a, '|';
''',
    'inherited-interface-alias-tables': br'''<?php
interface Tag157 { public function ping(); }
class Base157 implements Tag157 { public $data; public function ping() { echo 'BAD|'; return 0; } }
class Middle157 extends Base157 { public $tail = 0; }
class Leaf157 extends Middle157 {}
function outer157($x): TypeError { return new TypeError('outer', 7); }
$live = [1]; $snapshot = $live; $left = new Leaf157; $right = new Leaf157; $left->data =& $live; $right->data = [2];
$a = outer157($left); $b = outer157($right); $weak = WeakReference::create($left);
echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
$live = [3]; $snapshot[0] = 99; echo 'M|', $a <=> $b, ':', $snapshot[0], ':', $left->data[0], '|';
$live = [2]; $sa = (string)$a; $sb = (string)$b; echo 'E|', (int)($sa === $sb), ':', $a <=> $b, '|';
foreach ($left as $ignored) {} foreach ($right as $ignored) {}
$viewLeft = (array)$left; $viewRight = (array)$right; $left = null; echo 'H|', (int)($weak->get() !== null), ':', $a <=> $b, '|';
$live = [4]; echo 'R|', $viewLeft['data'][0], ':', $viewRight['data'][0], ':', $a <=> $b, '|';
$a = null; echo 'D|', (int)($weak->get() === null), '|';
''',
    'inherited-cycle-no-traps': br'''<?php
class Base157 { public $value = 0; public $next = null; public function __isset(string $name): bool { echo 'BAD|'; return false; } }
class Middle157 extends Base157 { public function unused() { echo 'BAD|'; } }
class Leaf157 extends Middle157 { public $tail = 0; }
function outer157($x): Error { return new Error('outer', 7); }
$left = new Leaf157; $right = new Leaf157; $left->value = 1; $right->value = 2; $left->next = $left; $right->next = $right;
$a = outer157($left); $b = outer157($right); echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';
$left->value = 2; $hold = 'hold'; echo 'C|'; $site = __LINE__ + 1;
try { try { $hold = $a <=> $b; echo 'BAD|'; } finally { echo 'F|', $hold, '|'; } }
catch (Error $e) { echo get_class($e), ':', $e->getMessage(), ':', (int)($e->getFile() === __FILE__), ':', (int)($e->getLine() === $site), ':', (int)($e->getTrace() === []), '|'; }
$right->next = $left; echo 'I|', $a <=> $b, ':', (int)($a == $b), '|';
$left->value = 1; echo 'R|', $a <=> $b, ':', $b <=> $a, '|';
''',
    'long-inherited-public-path': b'''<?php
class Parent157_0 { public $value = 0; }
''' + b''.join(('class Parent157_' + str(i) + ' extends Parent157_' + str(i - 1) + ' {}\n').encode()
    for i in range(1, 19)) + br'''
function outer157($x): Exception { return new Exception('outer', 7); }
$left = new Parent157_18; $right = new Parent157_18; $left->value = 1; $right->value = 2;
$a = outer157($left); $b = outer157($right); echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';
$left->value = 2; echo 'E|', $a <=> $b, '|';
''',
    'inherited-private-layout-control': br'''<?php
class Base157 { private $hidden = 0; }
class Leaf157 extends Base157 { public $value = 0; }
function outer157($x): Exception { return new Exception('outer', 7); }
$left = new Leaf157; $right = new Leaf157; $left->value = 1; $right->value = 2;
$a = outer157($left); $b = outer157($right); echo 'B|', $a <=> $b, '|';
''',
    'stdclass-parent-control': br'''<?php
class Leaf157 extends stdClass { public $value = 0; public function unused() { echo 'BAD|'; } }
function outer157($x): Exception { return new Exception('outer', 7); }
$left = new Leaf157; $right = new Leaf157; $left->value = 1; $right->value = 2;
$a = outer157($left); $b = outer157($right); echo 'B|', $a <=> $b, '|';
''',
}
