"""Frozen base Throwable fallback witnesses; ordinary catchable cycles only."""

CASES = {
    'warm-array-cell-snapshot': br'''<?php
function exception152($x): Exception { return new Exception('same', 7); }
$live = [1]; $snapshot = [1]; $a = exception152([&$live, $snapshot]); $b = exception152([[2], [1]]);
echo 'C|', $a <=> $b, ':', $b <=> $a, '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';
$snapshot[0] = 9; $live = [3]; echo 'M|', $snapshot[0], ':', $a <=> $b, '|';
$live = [2]; $api = $a->getTrace(); echo 'E|', $a <=> $b, ':', $api[0]['args'][0][0][0], ':', $api[0]['args'][0][1][0], '|';
$live = [7]; echo 'R|', $a <=> $b, ':', $api[0]['args'][0][0][0], ':', $api[0]['args'][0][1][0], '|';
''',
    'prefix-cache-skips-methods': br'''<?php
class Later152 { public $value = 0; public function __toString() { echo 'BAD|'; return 'x'; } }
function error152($x, $message): Error { return new Error($message, 7); }
$left = new Later152; $right = new Later152; $left->value = 1; $right->value = 2;
$a = error152($left, 'a'); $b = error152($right, 'b'); echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
$a = error152($left, 'same'); $b = error152($right, 'same'); $sa = (string)$a;
echo 'W|', $a <=> $b, ':', $b <=> $a, '|';
echo 'A|', [0, $a, new Later152] <=> [0, $b, 'x'], '|';
''',
    'count-key-skips-cycles': br'''<?php
class Tail152 { public function __toString() { echo 'BAD|'; return 'x'; } }
function exception152($x): Exception { return new Exception('same', 7); }
$left = new stdClass; $right = new stdClass; $left->first = 1; $right->first = 1; $left->next = $left; $right->next = $right; $right->extra = 0;
$a = exception152($left); $b = exception152($right); echo 'C|', $a <=> $b, ':', $b <=> $a, '|';
$u = new stdClass; $v = new stdClass; $u->alpha = 1; $v->beta = 1; $u->next = $u; $v->next = $v;
$c = exception152($u); $d = exception152($v); echo 'K|', $c <=> $d, ':', $d <=> $c, '|';
$sc = (string)$c; $sd = (string)$d; echo 'W|', (int)($sc === $sd), ':', $c <=> $d, '|';
echo 'A|', [0, $c, new Tail152] <=> [0, $d, 'x'], '|';
''',
    'array-cycle-before-count': br'''<?php
function error152($x): Error { return new Error('same', 7); }
$left = []; $right = []; $tail = ['next' => 0, 'extra' => 0]; $left['next'] =& $left; $right['next'] =& $tail;
$a = error152($left); $b = error152($right); $sa = (string)$a; $sb = (string)$b; $hold = 'hold'; echo 'W|', (int)($sa === $sb), '|B|'; $site = __LINE__ + 1;
try { try { $hold = $a <=> $b; } finally { echo 'F|', $hold, '|'; } }
catch (Error $e) { echo get_class($e), ':', $e->getMessage(), ':', (int)($e->getFile() === __FILE__), ':', (int)($e->getLine() === $site), ':', (int)($e->getTrace() === []), '|'; }
echo 'R|', $b <=> $a, ':', (int)($a > $b), ':', (int)($a >= $b), '|';
$left = ['next' => 0, 'extra' => 0]; echo 'M|', $a <=> $b, ':', (int)($a == $b), '|';
''',
    'reached-method-control': br'''<?php
class Later152 { public $value = 0; public function __toString() { echo 'BAD|'; return 'x'; } }
function error152($x): Error { return new Error('same', 7); }
$left = new Later152; $right = new Later152; $left->value = 1; $right->value = 2;
$a = error152($left); $b = error152($right); echo 'B|', $a <=> $b, '|';
''',
    'linked-base-control': br'''<?php
function exception152($x, $previous): Exception { return new Exception('same', 7, $previous); }
$left = new stdClass; $right = new stdClass; $left->value = 1; $right->value = 2; $left->next = $left; $right->next = $right;
$p = new Exception('inner', 1); $a = exception152($left, $p); $b = exception152($right, $p); echo 'B|', $a <=> $b, '|';
''',
}
