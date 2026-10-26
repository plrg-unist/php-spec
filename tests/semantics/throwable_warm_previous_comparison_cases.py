"""Warm physical caches within finite builtin Throwable previous chains."""

CASES = {
    'root-cache-collision': br'''<?php
$a = new Exception('top', 7, new Exception('inner', 1)); $b = new Exception('top', 7, new Exception('inner', 2));
echo 'B|', $a <=> $b, '|';
$sa = $a->__toString(); echo 'W|', $a <=> $b, ':', $b <=> $a, '|';
$sb = $b->__toString(); echo 'E|', (int)($sa === $sb), ':', $a <=> $b, ':', $b <=> $a, '|';
''',
    'child-cache-collision': br'''<?php
$pa = new Exception('inner', 1); $pb = new Exception('inner', 2); $a = new Exception('top', 7, $pa); $b = new Exception('top', 7, $pb);
echo 'B|', $a <=> $b, '|';
$sa = $pa->__toString(); echo 'W|', $a <=> $b, ':', $b <=> $a, '|';
$sb = $pb->__toString(); echo 'E|', (int)($sa === $sb), ':', $a <=> $b, ':', $b <=> $a, '|';
''',
    'equal-seven': br'''<?php
$a = new Exception('top', 7, new Exception('inner', 1)); $b = new Exception('top', 7, new Exception('inner', 1));
$a->__toString(); $b->__toString();
echo 'B|', (int)($a == $b), (int)($a != $b), (int)($a < $b), (int)($a <= $b), (int)($a > $b), (int)($a >= $b), ':', $a <=> $b, ':', (int)($a === $b), '|';
''',
    'error-cache-collision': br'''<?php
$a = new Error('top', 7, new Error('inner', 1)); $b = new Error('top', 7, new Error('inner', 2));
$sa = $a->__toString(); $sb = $b->__toString();
echo 'B|', (int)($sa === $sb), ':', $a <=> $b, ':', $b <=> $a, '|';
''',
    'aggregate-tail': br'''<?php
class Tail135 { public function __toString(): string { echo 'CAST|'; return 'x'; } }
$a = new Exception('top', 7, new Exception('inner', 1)); $b = new Exception('top', 7, new Exception('inner', 1)); $c = new Exception('top', 7, new Exception('inner', 2)); $tail = new Tail135;
$a->__toString(); $b->__toString(); $c->__toString();
echo 'B|', $a <=> $b, ':', $a <=> $c, '|';
echo 'E:', [$a, $tail] <=> [$b, 'x'], '|';
echo 'N:', [$a, $tail] <=> [$c, 'x'], '|';
''',
    'warm-nonempty-control': br'''<?php
function mk135($p): Exception { return new Exception('top', 7, $p); }
$pa = new Exception('inner', 1); $pb = new Exception('inner', 2); $a = mk135($pa); $b = mk135($pb);
$a->__toString(); $b->__toString();
echo 'B|', $a <=> $b, '|';
''',
    'warm-mixed-control': br'''<?php
$a = new Exception('top', 7, new Exception('inner', 1)); $b = new Exception('top', 7, new Error('inner', 1));
$a->__toString(); $b->__toString();
echo 'B|', $a <=> $b, '|';
''',
    'cold-previous-control': br'''<?php
$a = new Exception('top', 7, new Exception('inner', 1)); $b = new Exception('top', 7, new Exception('inner', 2));
echo 'B|', $a <=> $b, '|';
''',
    'warm-no-previous-control': br'''<?php
$a = new Exception('top', 7); $b = new Exception('top', 7);
$a->__toString(); $b->__toString();
echo 'B|', $a <=> $b, '|';
''',
}
