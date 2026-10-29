"""Frozen native-first comparisons across exact builtin Throwable classes."""

CASES = {
    'exception-lineage': br'''<?php
$e = new Exception('same', 7); $r = new RuntimeException('same', 7); $x = new ErrorException('same', 7, 8); $g = new ClosedGeneratorException('same', 7);
echo 'B|', $r<=>$e, ':', $e<=>$r, '|', $x<=>$e, ':', $e<=>$x, '|', $g<=>$e, ':', $e<=>$g, '|';
''',
    'error-lineage': br'''<?php
$e = new Error('same', 7); $c = new CompileError('same', 7); $p = new ParseError('same', 7); $t = new TypeError('same', 7); $a = new ArgumentCountError('same', 7);
echo 'P|', $c<=>$e, ':', $p<=>$c, ':', $t<=>$e, ':', $a<=>$t, '|';
$v = new ValueError('same', 7); $h = new ArithmeticError('same', 7); $d = new DivisionByZeroError('same', 7); $m = new UnhandledMatchError('same', 7); $s = new AssertionError('same', 7);
echo 'S|', $v<=>$t, ':', $h<=>$e, ':', $d<=>$h, ':', $m<=>$v, ':', $s<=>$m, '|';
''',
    'seven-operators': br'''<?php
$a = new TypeError('same', 7); $b = new ValueError('same', 7);
echo 'B|', (int)($a==$b), (int)($a!=$b), (int)($a<$b), (int)($a<=$b), (int)($a>$b), (int)($a>=$b), ':', $a<=>$b, ':', $b<=>$a, '|';
echo 'S|', (int)($a===$b), ':', (int)($a!==$b), '|';
''',
    'severity-warm-previous': br'''<?php
$p = new Exception('inner', 1); $q = new Error('inner', 2); $a = new ErrorException('same', 7, 8, 'custom.php', -2, $p); $b = new RuntimeException('same', 7, $q);
echo 'B|', $a<=>$b, ':', $b<=>$a, ':', $a->getSeverity(), '|';
$a->__toString(); $b->__toString(); echo 'W|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'cyclic-tail-skip': br'''<?php
class Bomb143 { public function __toString(): string { echo 'BAD|'; return 'x'; } }
function parse143($x): ParseError { return new ParseError('same', 7); }
function compile143($x): CompileError { return new CompileError('same', 7); }
$left = new stdClass; $right = new stdClass; $left->self = $left; $right->self = $right; $a = parse143([$left, new Bomb143]); $b = compile143([$right, new Bomb143]);
echo 'B|', $a<=>$b, ':', $b<=>$a, '|';
echo 'A|', [0,$a,new Bomb143]<=>[0,$b,'x'], '|';
''',
    'same-kind-control': br'''<?php
$a = new RuntimeException('same', 7); $b = new RuntimeException('same', 7);
echo 'B|', $a<=>$b, ':', (int)($a==$b), '|';
''',
    'old-cross-kind-control': br'''<?php
$a = new Exception('same', 7); $b = new Error('same', 7);
echo 'B|', $a<=>$b, ':', $b<=>$a, '|';
''',
}
