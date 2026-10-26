"""Same-kind builtin Throwable comparisons after a real string-cache write."""

CASES = {
    'exception-warm-operators': br'''<?php
$a = new Exception('same', 7); $b = new Exception('same', 7);
echo 'B|', (int)($a==$b), ':', $a<=>$b, '|';
$a->__toString();
echo 'W|', (int)($a==$b), (int)($a!=$b), (int)($a<$b), (int)($a<=$b), (int)($a>$b), (int)($a>=$b), ':', $a<=>$b, ':', $b<=>$a, '|';
$b->__toString();
echo 'E|', (int)($a==$b), ':', $a<=>$b, ':', (int)($a===$b), '|';
''',
    'error-warm-tail': br'''<?php
class Tail132 { public function __toString(): string { echo 'CAST|'; return 'x'; } }
$a = new Error('same', 7); $b = new Error('same', 7); $later = new Tail132;
$a->__toString();
echo 'N:', [$a,$later]<=>[$b,'x'], '|';
$b->__toString();
echo 'E:', $a<=>$b, ':', (int)($a===$b), '|';
echo 'T:', [$a,$later]<=>[$b,'x'], '|';
''',
    'cache-before-line': br'''<?php
// padding 2
// padding 3
// padding 4
// padding 5
// padding 6
// padding 7
// padding 8
$a = new Exception('same', 7);
$b = new Exception('same', 7);
echo 'B|', $a<=>$b, ':'; $a->__toString(); $b->__toString(); echo $a<=>$b, ':', $b<=>$a, '|';
''',
    'empty-message': br'''<?php
$a = new Exception; $b = new Exception;
$a->__toString(); $b->__toString();
echo 'B|', (int)($a==$b), ':', $a<=>$b, '|';
''',
    'warm-nonempty-trace-control': br'''<?php
function ex132($x): Exception { return new Exception('same', 7); }
$a = ex132(1); $b = ex132(1); $a->__toString();
echo 'B|', $a<=>$b, '|';
''',
    'warm-cross-kind-control': br'''<?php
$a = new Exception('same', 7); $b = new Error('same', 7); $a->__toString();
echo 'B|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'cold-baseline': br'''<?php
$a = new Exception('same', 7); $b = new Exception('same', 7);
echo 'B|', $a<=>$b, '|';
''',
}
