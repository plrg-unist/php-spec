"""Frozen standalone builtin Throwable traces without a previous carrier."""

CASES = {
    'object-trace-before-severity': br'''<?php
$severity151 = 9;
function ee151($x): ErrorException { global $severity151; return new ErrorException('same', 7, $severity151, __FILE__, 20); }
$left = new stdClass; $right = new stdClass; $left->value = 1; $right->value = 2;
$a = ee151($left); $severity151 = 1; $b = ee151($right);
echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';
$left->value = 3; echo 'M|', $a <=> $b, ':', $b <=> $a, '|';
$left->value = 2; echo 'E|', $a <=> $b, '|';
''',
    'array-cell-retarget-snapshot': br'''<?php
function run151($x): RuntimeException { return new RuntimeException('same', 7); }
$value = [1]; $a = run151([&$value, $value]); $b = run151([[2], [1]]);
echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';
$value = [3]; echo 'M|', $a <=> $b, '|';
$value = [2]; $saved = $a->getTrace(); echo 'E|', $a <=> $b, ':', $saved[0]['args'][0][0][0], ':', $saved[0]['args'][0][1][0], '|';
$value = [7]; echo 'R|', $a <=> $b, ':', $saved[0]['args'][0][0][0], ':', $saved[0]['args'][0][1][0], '|';
''',
    'ordinary-cycle-finally-recovery': br'''<?php
function type151($x): TypeError { return new TypeError('same', 7); }
$left = new stdClass; $right = new stdClass; $left->next = $left; $right->next = $right;
$a = type151($left); $b = type151($right); $hold = 'hold';
echo 'B|'; $site = __LINE__ + 1;
try { try { $hold = $a <=> $b; } finally { echo 'F|', $hold, '|'; } }
catch (Error $e) { echo get_class($e), ':', $e->getMessage(), ':', (int)($e->getFile() === __FILE__), ':', (int)($e->getLine() === $site), ':', (int)($e->getTrace() === []), '|'; }
$right->next = $left; echo 'I|', $a <=> $b, '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';
''',
    'warm-cache-skips-callback-payload': br'''<?php
class Later151 { public $value = 0; public function __toString() { echo 'BAD|'; return 'x'; } }
function cache151($x): RuntimeException { return new RuntimeException('same', 7); }
$left = new Later151; $right = new Later151; $left->value = 1; $right->value = 2;
$a = cache151($left); $b = cache151($right); $sa = (string)$a;
echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
echo 'A|', [0, $a, new Later151] <=> [0, $b, 'x'], '|';
''',
    'reached-callback-control': br'''<?php
class Callback151 { public $value = 0; public function __toString() { echo 'BAD|'; return 'x'; } }
function callback151($x): TypeError { return new TypeError('same', 7); }
$left = new Callback151; $right = new Callback151; $left->value = 1; $right->value = 2;
$a = callback151($left); $b = callback151($right);
echo 'B|', $a <=> $b, '|';
''',
    'base-legacy-control': br'''<?php
function base151($x): Exception { return new Exception('same', 7); }
$left = new stdClass; $right = new stdClass; $left->value = 1; $right->value = 2; $left->next = $left; $right->next = $right;
$a = base151($left); $b = base151($right);
echo 'B|', $a <=> $b, '|';
''',
}
