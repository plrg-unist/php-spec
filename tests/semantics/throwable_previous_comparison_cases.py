"""Cold builtin Throwable comparison through finite previous chains."""

CASES = {
    'equal-distinct': br'''<?php
$a = new Exception('top', 7, new Exception('inner', 3)); $b = new Exception('top', 7, new Exception('inner', 3));
echo 'B|', (int)($a == $b), (int)($a != $b), (int)($a < $b), (int)($a <= $b), (int)($a > $b), (int)($a >= $b), ':', $a <=> $b, ':', (int)($a === $b), '|';
''',
    'inner-order': br'''<?php
$a = new Exception('top', 7, new Exception('a', 3)); $b = new Exception('top', 7, new Exception('z', 3)); $c = new Exception('top', 7, new Exception('a', 4));
echo 'B|', $a <=> $b, ':', $b <=> $a, ':', $a <=> $c, ':', $c <=> $a, '|';
''',
    'null-shared': br'''<?php
$p = new Exception('inner', 3);
$none = new Exception('top', 7); $some = new Exception('top', 7, $p); $same = new Exception('top', 7, $p);
echo 'B|', $none <=> $some, ':', $some <=> $none, ':', $some <=> $same, '|';
''',
    'depth-tail': br'''<?php
class Tail134 { public function __toString(): string { echo 'CAST|'; return 'x'; } }
$a = new Exception('top', 7, new Exception('middle', 5, new Exception('leaf', 1))); $b = new Exception('top', 7, new Exception('middle', 5, new Exception('leaf', 1))); $c = new Exception('top', 7, new Exception('middle', 5, new Exception('zleaf', 1))); $tail = new Tail134;
echo 'B|', $a <=> $b, ':', $a <=> $c, '|';
echo 'E:', [$a, $tail] <=> [$b, 'x'], '|';
echo 'N:', [$a, $tail] <=> [$c, 'x'], '|';
''',
    'error-chain': br'''<?php
$a = new Error('top', 7, new Error('inner', 3)); $b = new Error('top', 7, new Error('inner', 3)); $c = new Error('top', 7, new Error('later', 3));
echo 'B|', $a <=> $b, ':', $a <=> $c, ':', $c <=> $a, '|';
''',
    'warm-control': br'''<?php
$a = new Exception('top', 7, new Exception('inner', 3)); $b = new Exception('top', 7, new Exception('inner', 3));
$a->__toString();
echo 'B|', $a <=> $b, '|';
''',
    'nonempty-control': br'''<?php
function make134($p): Exception { return new Exception('top', 7, $p); }
$p = new Exception('inner', 3); $a = make134($p); $b = make134($p);
echo 'B|', $a <=> $b, '|';
''',
    'mixed-link-control': br'''<?php
$a = new Exception('top', 7, new Exception('inner', 3)); $b = new Exception('top', 7, new Error('inner', 3));
echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
''',
}
