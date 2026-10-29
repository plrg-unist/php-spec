"""Frozen native-first same-kind comparisons for builtin Throwable classes."""

CASES = {
    'exception-kind-equality': br'''<?php
$a = new RuntimeException('same', 7); $b = new RuntimeException('same', 7); $c = new ClosedGeneratorException('same', 7); $d = new ClosedGeneratorException('same', 7); $e = new ErrorException('same', 7, 8, 'f.php', 9); $f = new ErrorException('same', 7, 8, 'f.php', 9);
echo 'B|', $a<=>$b, ':', $c<=>$d, ':', $e<=>$f, '|';
''',
    'error-kind-equality': br'''<?php
$a = new CompileError('same', 7); $b = new CompileError('same', 7); $c = new ParseError('same', 7); $d = new ParseError('same', 7); $e = new TypeError('same', 7); $f = new TypeError('same', 7); $g = new ArgumentCountError('same', 7); $h = new ArgumentCountError('same', 7);
echo 'P|', $a<=>$b, ':', $c<=>$d, ':', $e<=>$f, ':', $g<=>$h, '|';
$i = new ValueError('same', 7); $j = new ValueError('same', 7); $k = new ArithmeticError('same', 7); $l = new ArithmeticError('same', 7); $m = new DivisionByZeroError('same', 7); $n = new DivisionByZeroError('same', 7); $o = new UnhandledMatchError('same', 7); $p = new UnhandledMatchError('same', 7); $q = new AssertionError('same', 7); $r = new AssertionError('same', 7);
echo 'S|', $i<=>$j, ':', $k<=>$l, ':', $m<=>$n, ':', $o<=>$p, ':', $q<=>$r, '|';
''',
    'severity-operators-tail': br'''<?php
class Bomb144 { public function __toString(): string { echo 'BAD|'; return 'x'; } }
$a = new ErrorException('same', 7, 3, 'f.php', 9); $b = new ErrorException('same', 7, 4, 'f.php', 9); $c = new ErrorException('same', 7, 3, 'f.php', 9);
echo 'B|', (int)($a==$b), (int)($a!=$b), (int)($a<$b), (int)($a<=$b), (int)($a>$b), (int)($a>=$b), ':', $a<=>$b, ':', $b<=>$a, ':', $a<=>$c, '|';
$sa = $a->__toString(); $sb = $b->__toString(); $c->__toString(); echo 'W|', (int)($sa===$sb), ':', $a<=>$b, ':', $a<=>$c, '|';
echo 'A|', [0,$a,1]<=>[0,$c,3], ':', [0,$a,new Bomb144]<=>[0,$b,'x'], '|';
''',
    'type-trace-arrays': br'''<?php
function ty144($x): TypeError { return new TypeError('same', 7); }
$a = ty144([1]); $b = ty144([2]); $c = ty144([1,2]); $d = ty144([1=>1]);
echo 'V|', $a<=>$b, ':', $b<=>$a, '|C|', $a<=>$c, ':', $c<=>$a, '|K|', $a<=>$d, ':', $d<=>$a, '|';
$a->__toString(); $b->__toString(); echo 'W|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'runtime-warm-priority': br'''<?php
function run144($x): RuntimeException { return new RuntimeException('same', 7); }
$a = run144(9); $b = run144(10);
echo 'B|', $a<=>$b, ':', $b<=>$a, '|';
$a->__toString(); echo 'O|', $a<=>$b, ':', $b<=>$a, '|';
$b->__toString(); echo 'W|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'alias-control': br'''<?php
function ty144($x): TypeError { return new TypeError('same', 7); }
$v = 1; $a = ty144([&$v]); $b = ty144([1]);
echo 'B|', $a<=>$b, '|';
''',
    'cycle-control': br'''<?php
function ty144($x): TypeError { return new TypeError('same', 7); }
$a0 = new stdClass; $b0 = new stdClass; $a0->self = $a0; $b0->self = $b0; $a = ty144($a0); $b = ty144($b0);
echo 'B|'; try { echo $a<=>$b, '|'; } catch (Error $error) { echo 'E|', $error->getMessage(), '|'; }
''',
    'previous-control': br'''<?php
$p = new Exception('inner', 1); $a = new TypeError('same', 7, $p); $b = new TypeError('same', 7, $p);
echo 'B|', $a<=>$b, '|';
''',
    'old-exception-control': br'''<?php
$a = new Exception('same', 7); $b = new Exception('same', 7);
echo 'B|', $a<=>$b, '|';
''',
}
