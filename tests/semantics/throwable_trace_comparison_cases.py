"""Nonempty builtin Throwable traces with scalar argument snapshots."""

CASES = {
    'scalar-operators': br'''<?php
function trace130($x): Exception { return new Exception('same', 7); }
$a = trace130(1); $b = trace130(1); $c = trace130(2);
$d = trace130(1);
echo 'B|';
foreach ([[$a,$b],[$a,$c],[$c,$a],[$a,$d]] as [$x,$y]) {
    echo (int)($x==$y), (int)($x!=$y), (int)($x<$y), (int)($x<=$y), (int)($x>$y), (int)($x>=$y), ':', $x<=>$y, '|';
}
echo (int)($a===$b), '|';
''',
    'frame-count-and-caster': br'''<?php
class TraceTail130 { public function __toString(): string { echo 'CAST|'; return 'x'; } }
function trace130($x): Exception { return new Exception('same', 7); }
function outer130(): Exception { return trace130(1); }
$one = trace130(1); $two = outer130();
$equal = outer130(); $copy = outer130();
$later = new TraceTail130;
echo 'B|', $one<=>$two, ':', $two<=>$one, '|';
echo 'E:', [$equal,$later]<=>[$copy,'x'], '|';
echo 'N:', [$one,$later]<=>[$two,'x'], '|';
''',
    'error-scalar-args': br'''<?php
function error130($x): Error { return new Error('same', 7); }
$a = error130(null); $b = error130(null); $c = error130(false); $d = error130(1.5); $e = error130('x');
echo 'B|', (int)($a==$b), ':', $a<=>$b, '|';
echo 'F:', $a<=>$c, ':', $c<=>$a, '|';
echo 'D:', $c<=>$d, ':', $d<=>$c, '|';
echo 'S:', $d<=>$e, ':', $e<=>$d, '|';
''',
    'named-argument-key': br'''<?php
function named130($a, ...$rest): Exception { return new Exception('same', 7); }
$a = named130(a: 1, extra: 2); $b = named130(a: 1, extra: 2); $c = named130(a: 1, extra: 3); $d = named130(a: 1, other: 2);
echo 'B|', $a<=>$b, ':', $a<=>$c, ':', $c<=>$a, ':', $a<=>$d, ':', $d<=>$a, '|';
''',
    'empty-nonempty-trace': br'''<?php
function trace130($x): Exception { return new Exception('same', 7); }
$a = new Exception('same', 7); $b = trace130(1);
echo 'B|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'state-direct-array': br'''<?php
function trace130($x): Exception { return new Exception('same', 7); }
$a = trace130(1); $b = trace130(1);
$x = [$a, 1]; $y = [$b, 3];
echo 'B|', $a<=>$b, '|', $x<=>$y, '|';
''',
    'object-arg-control': br'''<?php
function trace130($x): Exception { return new Exception('same', 7); }
$object = new stdClass;
$a = trace130($object); $b = trace130($object);
echo 'B|', $a<=>$b, '|';
''',
    'array-arg-control': br'''<?php
function trace130($x): Exception { return new Exception('same', 7); }
$a = trace130([1]); $b = trace130([1]);
echo 'B|', $a<=>$b, '|';
''',
    'cold-baseline': br'''<?php
$a = new Exception('same'); $b = new Exception('same');
echo 'B|', $a<=>$b, '|';
''',
}
