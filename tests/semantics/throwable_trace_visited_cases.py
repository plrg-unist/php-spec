"""Frozen native-first decisions before unvisited captured payloads."""

CASES = {
    'array-count-skips-cycle': br'''<?php
function child147($x): TypeError { return new TypeError('inner',7); }
$lc = []; $rc = []; $lc['self'] =& $lc; $rc['self'] =& $rc;
$p = child147([$lc,9]); $q = child147([$rc]);
$a = new ErrorException('same',7,1,'f.php',9,$p); $b = new ErrorException('same',7,9,'f.php',9,$q);
echo 'B|', $a<=>$b, ':', $b<=>$a, '|';
$sa = $a->__toString(); $sb = $b->__toString(); echo 'W|', (int)($sa===$sb), ':', $a<=>$b, '|';
''',
    'array-key-skips-cycle': br'''<?php
class Tail147 { public function __toString(): string { echo 'BAD|'; return 'x'; } }
function child147($x): TypeError { return new TypeError('inner',7); }
$lc = []; $rc = []; $lc['self'] =& $lc; $rc['self'] =& $rc;
$p = child147([1=>$lc]); $q = child147([2=>$rc]);
$a = new RuntimeException('same',7,$p); $b = new RuntimeException('same',7,$q);
echo 'B|', (int)($a==$b), (int)($a!=$b), (int)($a<$b), (int)($a<=$b), (int)($a>$b), (int)($a>=$b), ':', $a<=>$b, ':', $b<=>$a, '|';
echo 'A|', [$a,new Tail147]<=>[$b,'x'], '|';
''',
    'array-live-leaf-skips-cycle': br'''<?php
function child147($x): TypeError { return new TypeError('inner',7); }
$lc = []; $rc = []; $lc['self'] =& $lc; $rc['self'] =& $rc; $first = 1;
$p = child147([&$first,$lc]); $q = child147([2,$rc]);
$a = new ErrorException('same',7,9,'f.php',9,$p); $b = new ErrorException('same',7,1,'f.php',9,$q);
echo 'B|', $a<=>$b, ':', $b<=>$a, '|';
$first = 3; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'object-identity-skips-cycle': br'''<?php
function child147($x): TypeError { return new TypeError('inner',7); }
$shared = new stdClass; $shared->self = $shared;
$p = child147($shared); $q = child147($shared);
$a = new ErrorException('same',7,3,'f.php',9,$p); $b = new ErrorException('same',7,3,'f.php',9,$q);
echo 'B|', $a<=>$b, '|';
$sa = $a->__toString(); $sb = $b->__toString(); echo 'W|', (int)($sa===$sb), ':', $a<=>$b, '|';
echo 'A|', [0,$a,1]<=>[0,$b,3], '|';
''',
    'object-class-skips-cycle-callback': br'''<?php
class Left147 { public $next = null; public function __toString(): string { echo 'BAD|'; return 'x'; } }
class Right147 { public $next = null; public function __toString(): string { echo 'BAD|'; return 'x'; } }
class Tail147 { public function __toString(): string { echo 'BAD|'; return 'x'; } }
function child147($x): TypeError { return new TypeError('inner',7); }
$left = new Left147; $right = new Right147; $left->next = $left; $right->next = $right;
$p = child147($left); $q = child147($right);
$a = new RuntimeException('same',7,$p); $b = new RuntimeException('same',7,$q);
echo 'B|', (int)($a==$b), (int)($a!=$b), (int)($a<$b), (int)($a<=$b), (int)($a>$b), (int)($a>=$b), ':', $a<=>$b, ':', $b<=>$a, '|';
echo 'A|', [$a,new Tail147]<=>[$b,'x'], '|';
''',
    'object-leaf-skips-unsupported': br'''<?php
class Callback147 { public function __toString(): string { echo 'BAD|'; return 'x'; } }
function child147($x): TypeError { return new TypeError('inner',7); }
$left = new stdClass; $right = new stdClass; $left->a = 1; $right->a = 2; $left->tail = new Callback147; $right->tail = new Callback147;
$p = child147($left); $q = child147($right);
$a = new ErrorException('same',7,9,'f.php',9,$p); $b = new ErrorException('same',7,1,'f.php',9,$q);
echo 'B|', $a<=>$b, ':', $b<=>$a, '|';
$left->a = 3; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'array-identity-skips-cycle': br'''<?php
function child147($x): TypeError { return new TypeError('inner',7); }
$cycle = []; $cycle['self'] =& $cycle;
$p = child147($cycle); $q = child147($cycle);
$a = new RuntimeException('same',7,$p); $b = new RuntimeException('same',7,$q);
echo 'B|', $a<=>$b, '|';
echo 'A|', [0,$a,1]<=>[0,$b,3], '|';
''',
    'root-cache-skips-trace-cycle': br'''<?php
class Tail147 { public function __toString(): string { echo 'BAD|'; return 'x'; } }
function root147($x): RuntimeException { global $previous; return new RuntimeException('same',7,$previous); }
$previous = new TypeError('inner',7); $left = new stdClass; $right = new stdClass; $left->self = $left; $right->self = $right;
$a = root147($left); $b = root147($right);
$a->__toString(); echo 'B|', $a<=>$b, ':', $b<=>$a, '|';
echo 'A|', [$a,new Tail147]<=>[$b,'x'], '|';
''',
    'cell-deref-identity-before-recursion': br'''<?php
function child147($x): TypeError { return new TypeError('inner',7); }
$left = new stdClass; $right = new stdClass; $lv = $left; $rv = $right; $left->link =& $lv; $right->link =& $lv;
$p = child147([&$lv]); $q = child147([&$rv]);
$a = new RuntimeException('same',7,$p); $b = new RuntimeException('same',7,$q);
echo 'B|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'same-nan-cell-before-cycle': br'''<?php
function child147($x): TypeError { return new TypeError('inner',7); }
$left = new stdClass; $right = new stdClass; $left->self = $left; $right->self = $right; $nan = NAN;
$p = child147([&$nan,$left]); $q = child147([&$nan,$right]);
$a = new RuntimeException('same',7,$p); $b = new RuntimeException('same',7,$q);
echo 'B|', (int)($a==$b), (int)($a!=$b), ':', $a<=>$b, ':', $b<=>$a, '|';
''',
    'plain-inline-leaf-skips-cycle': br'''<?php
class Plain147 { public int $first = 0; public $next = null; }
function child147($x): TypeError { return new TypeError('inner',7); }
$left = new Plain147; $right = new Plain147; $left->first = 1; $right->first = 2; $left->next = $left; $right->next = $right;
$p = child147($left); $q = child147($right);
$a = new ErrorException('same',7,9,'f.php',9,$p); $b = new ErrorException('same',7,1,'f.php',9,$q);
echo 'B|', $a<=>$b, ':', $b<=>$a, '|';
$sa = $a->__toString(); $sb = $b->__toString(); echo 'W|', (int)($sa===$sb), ':', $a<=>$b, '|';
$left->first = 3; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
''',
}
