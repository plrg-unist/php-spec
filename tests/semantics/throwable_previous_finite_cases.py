"""Frozen originals for finite canonical previous paths and deep root entry."""

CASES = {
    'long-cold-exception': br'''<?php
$a = new Exception('leaf', 1); $b = new Exception('leaf', 2);
for ($i = 0; $i < 24; $i++) { $a = new Exception('node', 7, $a); $b = new Exception('node', 7, $b); }
echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
echo 'A|', [0, $a, 1] <=> [0, $b, 0], '|';
''',
    'long-warm-error': br'''<?php
$a = new Error('leaf', 1); $b = new Error('leaf', 2);
for ($i = 0; $i < 24; $i++) { $a = new Error('node', 7, $a); $b = new Error('node', 7, $b); }
$sa = (string)$a; $sb = (string)$b;
echo 'B|', (int)($sa === $sb), ':', $a <=> $b, ':', $b <=> $a, '|';
echo 'A|', [$a, 1] <=> [$b, 0], '|';
''',
    'long-captured-cycle-recovery': br'''<?php
function child150($x): TypeError { return new TypeError('inner', 7); }
$left = new stdClass; $right = new stdClass; $left->value = 1; $right->value = 2;
$a = child150($left); $b = child150($right);
for ($i = 0; $i < 24; $i++) { $a = new ErrorException('node', 7, 9, __FILE__, 20, $a); $b = new ErrorException('node', 7, 1, __FILE__, 20, $b); }
echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';
$left->value = 0; $right->value = 0; $left->next = $left; $right->next = $right; $hold = 'hold';
echo 'C|'; $site = __LINE__ + 1;
try { try { $hold = $a <=> $b; } finally { echo 'F|', $hold, '|'; } }
catch (Error $e) { echo get_class($e), ':', $e->getMessage(), ':', (int)($e->getFile() === __FILE__), ':', (int)($e->getLine() === $site), ':', (int)($e->getTrace() === []), '|'; }
$right->next = $left; echo 'I|', $a <=> $b, '|';
''',
    'deep-base-class-skip': br'''<?php
class Tail150 { public function __toString() { echo 'BAD|'; return 'tail'; } }
function exception150($x): Exception { return new Exception('same', 7); }
function error150($x): Error { return new Error('same', 7); }
$left = new stdClass; $right = new stdClass; $left->next = $left; $right->next = $right;
$a = exception150($left); $b = error150($right); $la = [$a, new Tail150]; $lb = [$b, 'tail'];
for ($i = 0; $i < 24; $i++) { $la = [$la]; $lb = [$lb]; }
echo 'B|', $la <=> $lb, ':', $lb <=> $la, ':', (int)($la < $lb), ':', (int)($la > $lb), '|';
''',
}
