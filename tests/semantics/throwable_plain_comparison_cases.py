"""Cold builtin Throwable comparisons through their physical declared slots."""

CASES = {
    'exception-signs': br'''<?php
$a = new Exception('same', 7); $b = new Exception('same', 7);
$c = new Exception('later', 7); $d = new Exception('same', 9);
echo 'B|';
foreach ([[$a,$b],[$a,$c],[$a,$d]] as [$x,$y]) {
    echo (int)($x == $y), (int)($x != $y), (int)($x < $y), (int)($x <= $y), (int)($x > $y), (int)($x >= $y), ':', $x <=> $y, '|';
}
echo (int)($a === $b), '|';
echo (int)([$a,17] == [$b,17]), (int)([$a,17] == [$c,17]), '|';
''',
    'exception-line-and-tail': br'''<?php
$a = new Exception('same', 7); $b = new Exception('same', 7);
$c = new Exception('same', 7);
echo 'B|', $a <=> $b, ':', $a <=> $c, ':', $c <=> $a, '|';
echo 'A|', [$a, 1] <=> [$b, 3], ':', [$a, 3] == [$b, 3], '|';
echo 'I|', (int)($a === $b), ':', (int)($a === $a), '|';
''',
    'error-line-and-tail': br'''<?php
$a = new Error('same', 7); $b = new Error('same', 7);
$c = new Error('same', 7);
$d = new Error('later', 7);
echo 'B|', (int)($a==$b), (int)($a!=$b), (int)($a<$b), (int)($a<=$b), (int)($a>$b), (int)($a>=$b), ':', $a<=>$b, '|';
echo 'L:', $a<=>$c, ':', $c<=>$a, '|';
echo 'M:', $a<=>$d, '|';
echo 'A:', [$a, 1]<=>[$b, 3], ':', [$a, 3]==[$b, 3], '|';
echo 'I:', (int)($a===$b), ':', (int)($a===$a), '|';
''',
    'different-class-control': br'''<?php
$a = new Exception('same', 7); $b = new Error('same', 7);
echo 'B|', $a <=> $b, '|';
''',
    'previous-control': br'''<?php
$previous = new Exception('old');
$a = new Exception('same', 7, $previous); $b = new Exception('same', 7, $previous);
echo 'B|', $a <=> $b, '|';
''',
    'skip-later-caster': br'''<?php
class LaterCaster129 {
    public function __toString(): string { echo 'CAST|'; return 'x'; }
}
$a = new Exception('same'); $b = new Exception('same'); $c = new Exception('other');
$later = new LaterCaster129;
echo 'B|';
echo 'E:', [$a, $later] <=> [$b, 'x'], '|';
echo 'N:', [$a, $later] <=> [$c, 'x'], '|';
''',
    'warm-cache-control': br'''<?php
$a = new Exception('same'); $b = new Exception('same');
$cache = (string)$a;
echo 'B|', $a <=> $b, '|';
''',
    'nonempty-trace-control': br'''<?php
function make129(): Exception { return new Exception('same'); }
$a = make129(); $b = make129();
echo 'B|', $a <=> $b, '|';
''',
    'pending-notice-control': br'''<?php
set_error_handler(function (int $level, string $text): void { echo 'H|'; throw new Exception('stop'); });
$a = new Exception('same'); $b = new Exception('same');
echo 'B|';
try { echo [new stdClass, $a] <=> [1, $b], '|BAD'; }
catch (Exception $caught) { echo 'C|'; }
''',
    'state-direct-array': br'''<?php
$a = new Exception('same'); $b = new Exception('same');
$x = [$a, 1]; $y = [$b, 3];
echo 'B|', $a <=> $b, '|', $x <=> $y, '|';
''',
}
