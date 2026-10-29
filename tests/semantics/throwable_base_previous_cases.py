"""Frozen finite linked-base comparisons; no native Previous-cycle probes."""

CASES = {
    'root-trace-before-link-code': br'''<?php
class Tail153 { public function __toString() { echo 'BAD|'; return 'x'; } }
function exception153($x): Exception { global $previous153; return new Exception('same', 7, $previous153); }
$legacyP = new Exception('inner', 1); $legacyA = new Exception('legacy', 7, $legacyP); $legacyB = new Exception('legacy', 7, $legacyP);
echo 'L|', $legacyA <=> $legacyB, ':', (int)($legacyA == $legacyB), '|';
$p = new TypeError('inner', 9); $q = new TypeError('inner', 1);
$left = new stdClass; $right = new stdClass; $left->value = 1; $right->value = 2;
$previous153 = $p; $a = exception153($left); $previous153 = $q; $b = exception153($right);
echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
$left->value = 2; echo 'P|', $a <=> $b, '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';
$kept = $a->getPrevious(); unset($p); $previous153 = new TypeError('replacement', 0); echo 'O|', (int)($kept === $a->getPrevious()), ':', $kept->getCode(), '|';
echo 'A|', [0, $a, new Tail153] <=> [0, $b, 'x'], '|';
''',
    'previous-before-child-severity': br'''<?php
function child153($x): ErrorException { global $deep153, $severity153; return new ErrorException('child', 7, $severity153, __FILE__, 20, $deep153); }
$deepLeft = new TypeError('deep', 9); $deepRight = new TypeError('deep', 1);
$left = new stdClass; $right = new stdClass; $left->value = 1; $right->value = 2;
$deep153 = $deepLeft; $severity153 = 1; $p = child153($left); $deep153 = $deepRight; $severity153 = 9; $q = child153($right);
$a = new Error('same', 7, $p); $b = new Error('same', 7, $q);
echo 'T|', $a <=> $b, ':', $b <=> $a, '|';
$left->value = 2; echo 'P|', $a <=> $b, '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';
$shared = new stdClass; $shared->next = $shared;
$deep153 = $deepLeft; $severity153 = 9; $u = child153($shared); $severity153 = 1; $v = child153($shared);
$c = new Error('same', 7, $u); $d = new Error('same', 7, $v);
echo 'S|', $c <=> $d, ':', $d <=> $c, '|';
''',
    'linked-array-error-before-previous': br'''<?php
function exception153($x): Exception { global $previous153; return new Exception('same', 7, $previous153); }
$p = new TypeError('inner', 9); $q = new TypeError('inner', 1);
$left = []; $right = []; $tail = ['next' => 0, 'extra' => 0]; $left['next'] =& $left; $right['next'] =& $tail;
$previous153 = $p; $a = exception153($left); $previous153 = $q; $b = exception153($right); $sa = (string)$a; $sb = (string)$b; $hold = 'hold'; echo 'W|', (int)($sa === $sb), '|B|'; $site = __LINE__ + 1;
try { try { $hold = $a <=> $b; } finally { echo 'F|', $hold, '|'; } }
catch (Error $e) { echo get_class($e), ':', $e->getMessage(), ':', (int)($e->getFile() === __FILE__), ':', (int)($e->getLine() === $site), ':', (int)($e->getTrace() === []), '|'; }
echo 'R|', $b <=> $a, ':', (int)($a > $b), ':', (int)($a >= $b), '|';
$left = ['next' => 0, 'extra' => 0]; echo 'M|', $a <=> $b, ':', $b <=> $a, '|';
''',
    'equal-four-table-continuation': br'''<?php
class Tail153 { public function __toString() { echo 'BAD|'; return 'x'; } }
function child153($x): Exception { return new Exception('inner', 1); }
function error153($x): Error { global $previous153; return new Error('same', 7, $previous153); }
$rootLeft = new stdClass; $rootRight = new stdClass; $rootLeft->value = 0; $rootRight->value = 0;
$childLeft = new stdClass; $childRight = new stdClass; $childLeft->value = 1; $childRight->value = 1;
$p = child153($childLeft); $q = child153($childRight);
$previous153 = $p; $a = error153($rootLeft); $previous153 = $q; $b = error153($rootRight);
echo 'E|', $a <=> $b, ':', (int)($a == $b), '|A|', [0, $a, 1] <=> [0, $b, 3], '|';
$childRight->value = 3; echo 'M|', $a <=> $b, ':', $b <=> $a, '|N|', [0, $a, new Tail153] <=> [0, $b, 'x'], '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';
$childRight->value = 1; echo 'Q|', $a <=> $b, ':', [0, $a, 1] <=> [0, $b, 3], '|';
''',
    'reached-child-method-control': br'''<?php
class Later153 { public $value = 0; public function __toString() { echo 'BAD|'; return 'x'; } }
function child153($x): TypeError { return new TypeError('inner', 1); }
$left = new Later153; $right = new Later153; $left->value = 1; $right->value = 2; $p = child153($left); $q = child153($right);
$a = new Exception('same', 7, $p); $b = new Exception('same', 7, $q); echo 'B|', $a <=> $b, '|';
''',
    'captured-throwable-control': br'''<?php
function error153($x): Error { global $previous153; return new Error('same', 7, $previous153); }
$previous153 = new Exception('inner', 1); $captured = new TypeError('captured', 2); $a = error153($captured); $b = error153($captured);
echo 'B|', $a <=> $b, '|';
''',
}
