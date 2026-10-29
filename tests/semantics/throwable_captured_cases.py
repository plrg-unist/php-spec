"""Frozen captured builtin-Throwable comparisons; Previous paths stay acyclic."""

CASES = {
    'captured-cache-before-severity': br'''<?php
function outer154($x): ErrorException { global $severity154; return new ErrorException('outer', 7, $severity154, __FILE__, 20); }
$p = new ErrorException('inner', 7, 1, __FILE__, 10); $q = new ErrorException('inner', 7, 9, __FILE__, 10);
$severity154 = 9; $a = outer154($p); $severity154 = 1; $b = outer154($q);
echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';
$sp = (string)$p; echo 'C1|', $a <=> $b, ':', $b <=> $a, '|';
$sq = (string)$q; echo 'C2|', (int)($sp === $sq), ':', $a <=> $b, '|';
''',
    'captured-live-graph-cow': br'''<?php
function child154($x): TypeError { global $previous154; return new TypeError('inner', 7, $previous154); }
function outer154($x): Exception { return new Exception('outer', 7); }
$previous154 = new Exception('leaf', 1); $seed = [1];
$left = new stdClass; $right = new stdClass; $left->data = $seed; $right->data = [2];
$p = child154($left); $q = child154($right);
$live = $p; $snapshot = $p; $a = outer154([&$live, $snapshot]); $b = outer154([$q, $p]);
echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';
$seed[0] = 99; echo 'C|', $seed[0], ':', $left->data[0], ':', $a <=> $b, '|';
$left->data[0] = 3; echo 'M|', $a <=> $b, ':', $b <=> $a, '|';
$left->data[0] = 2; echo 'E|', $a <=> $b, '|';
$view = $a->getTrace(); $live = $q; $view[0]['args'][0][1] = $q;
echo 'R|', $a <=> $b, ':', (int)($a->getTrace()[0]['args'][0][0] === $q), ':', (int)($a->getTrace()[0]['args'][0][1] === $p), '|';
$live = new ValueError('replacement', 7); echo 'K|', $a <=> $b, ':', $b <=> $a, '|';
''',
    'captured-identity-class-cache-skips': br'''<?php
class Later154 { public $value = 0; public $next; public function __toString() { echo 'BAD|'; return 'x'; } }
class Tail154 { public function __toString() { echo 'BAD|'; return 'x'; } }
function child154($x): RuntimeException { return new RuntimeException('inner', 7); }
function other154($x): ValueError { return new ValueError('inner', 7); }
function outer154($x): TypeError { return new TypeError('outer', 7); }
$left = new Later154; $right = new Later154; $left->value = 1; $right->value = 2; $left->next = $left; $right->next = $right;
$p = child154($left); $q = other154($right);
$a = outer154($p); $b = outer154($q); echo 'K|', $a <=> $b, ':', $b <=> $a, '|';
$c = outer154($p); $d = outer154($p); echo 'I|', $c <=> $d, ':', (int)($c == $d), '|';
$ordinary = new stdClass; $ordinary->next = $ordinary; $e = outer154($p); $f = outer154($ordinary);
echo 'M|', $e <=> $f, ':', $f <=> $e, '|';
$r = child154($right); $g = outer154($p); $h = outer154($r); $sg = (string)$g;
echo 'C|', $g <=> $h, ':', $h <=> $g, '|A|', [0, $g, new Tail154] <=> [0, $h, 'x'], '|';
''',
    'captured-alias-recursion-recovery': br'''<?php
function outer154($x): Exception { return new Exception('same', 7); }
$left = null; $right = null; $a = outer154([&$left]); $b = outer154([&$right]);
$left = $a; $right = $b; $hold = 'hold'; echo 'B|'; $site = __LINE__ + 1;
try { try { $hold = $a <=> $b; echo 'BAD|'; } finally { echo 'F|', $hold, '|'; } }
catch (Error $e) { echo get_class($e), ':', $e->getMessage(), ':', (int)($e->getFile() === __FILE__), ':', (int)($e->getLine() === $site), ':', (int)($e->getTrace() === []), '|'; }
$right = $a; echo 'I|', $a <=> $b, ':', (int)($a == $b), '|';
$right = new Error('different', 1); echo 'K|', $a <=> $b, ':', $b <=> $a, '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';
''',
    'reached-captured-method-control': br'''<?php
class Later154 { public $value = 0; public function __toString() { echo 'BAD|'; return 'x'; } }
function child154($x): TypeError { return new TypeError('inner', 7); }
function outer154($x): Exception { return new Exception('outer', 7); }
$left = new Later154; $right = new Later154; $left->value = 1; $right->value = 2; $p = child154($left); $q = child154($right);
$a = outer154($p); $b = outer154($q); echo 'B|', $a <=> $b, '|';
''',
    'captured-object-scalar-control': br'''<?php
function outer154($x): Exception { return new Exception('outer', 7); }
$p = new TypeError('inner', 7); $a = outer154($p); $b = outer154('text');
echo 'B|', $a <=> $b, '|';
''',
}
