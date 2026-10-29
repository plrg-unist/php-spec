"""Frozen originals for reached ordinary recursion errors in previous traces."""

CASES = {
    'std-error-origin-trace': br'''<?php
function child148($x): TypeError { return new TypeError('inner', 7); }
function compare148($a, $b) { try { return $a <=> $b; } finally { echo 'F|'; } }
$left = new stdClass; $right = new stdClass; $left->next = $left; $right->next = $right;
$p = child148($left); $q = child148($right);
$a = new ErrorException('root', 7, 9, __FILE__, 20, $p); $b = new ErrorException('root', 7, 1, __FILE__, 20, $q);
echo 'B|';
try { echo compare148($a, $b), '|'; }
catch (Error $e) {
    echo get_class($e), ':', $e->getMessage(), ':', $e->getCode(), ':', (int)($e->getFile() === __FILE__), ':', $e->getLine(), ':', (int)($e->getPrevious() === null), '|';
    $t = $e->getTrace(); echo $t[0]['function'], ':', (int)($t[0]['args'][0] === $a), ':', (int)($t[0]['args'][1] === $b), '|';
}
''',
    'array-cycle-operators': br'''<?php
function child148($x): TypeError { return new TypeError('inner', 7); }
$left = []; $right = []; $left['next'] =& $left; $right['next'] =& $right;
$p = child148($left); $q = child148($right);
$a = new RuntimeException('root', 7, $p); $b = new RuntimeException('root', 7, $q);
echo 'B|';
try { echo (int)($a == $b); } catch (Error $e) { echo 'E'; }
try { echo (int)($a != $b); } catch (Error $e) { echo 'E'; }
try { echo (int)($a < $b); } catch (Error $e) { echo 'E'; }
try { echo (int)($a <= $b); } catch (Error $e) { echo 'E'; }
try { echo (int)($a > $b); } catch (Error $e) { echo 'E'; }
try { echo (int)($a >= $b); } catch (Error $e) { echo 'E'; }
try { echo $a <=> $b; } catch (Error $e) { echo 'E|', $e->getMessage(), '|'; }
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':';
try { echo $b <=> $a; } catch (Error $e) { echo 'E|'; }
''',
    'inline-cycle-recovery': br'''<?php
class Plain148 { public $first = 0; public $next; }
function child148($x): TypeError { return new TypeError('inner', 7); }
$left = new Plain148; $right = new Plain148; $left->next = $left; $right->next = $right;
$p = child148($left); $q = child148($right);
$a = new ErrorException('root', 7, 9, __FILE__, 20, $p); $b = new ErrorException('root', 7, 1, __FILE__, 20, $q);
echo 'B|';
try { echo $a <=> $b; } catch (Error $e) { echo 'E|', $e->getMessage(), '|'; }
$right->first = 1; echo 'M|', $a <=> $b, ':', $b <=> $a, '|';
$right->first = 0; $left->next = $right; echo 'I|', $a <=> $b, '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';
''',
    'aggregate-error-finally-cleanup': br'''<?php
class Guard148 { public function __destruct() { echo 'D|'; } }
class Tail148 { public function __toString() { echo 'T|'; return 'tail'; } }
function child148($x): TypeError { return new TypeError('inner', 7); }
function compare148($a, $b, $tail) {
    $guard = new Guard148;
    try { return [$a, $tail] <=> [$b, 'tail']; }
    finally { echo 'F|'; }
}
$left = new stdClass; $right = new stdClass; $left->next = $left; $right->next = $right;
$p = child148($left); $q = child148($right);
$a = new RuntimeException('root', 7, $p); $b = new RuntimeException('root', 7, $q); $tail = new Tail148;
echo 'B|';
try { echo compare148($a, $b, $tail); }
catch (Error $e) {
    echo 'E|', $e->getMessage(), '|';
    try { throw $e; } catch (Throwable $again) { echo 'R|', (int)($again === $e), '|'; }
}
$right->next = 0; echo 'M|', $a <=> $b, '|';
''',
}
