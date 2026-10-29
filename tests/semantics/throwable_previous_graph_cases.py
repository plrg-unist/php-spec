"""Frozen native-first finite live graphs inside builtin previous chains."""

CASES = {
    'std-live-cow-warm-tail': br'''<?php
class Tail146 { public function __toString(): string { echo 'BAD|'; return 'x'; } }
function child146($x): TypeError { return new TypeError('inner', 7); }
$source = [1,2]; $left = new stdClass; $right = new stdClass; $left->data = $source; $right->data = [1,3];
$p = child146($left); $q = child146($right);
$a = new ErrorException('same',7,9,'f.php',9,$p); $b = new ErrorException('same',7,1,'f.php',9,$q); $c = new ErrorException('same',7,9,'f.php',9,$q);
echo 'B|', $a<=>$b, ':', $b<=>$a, '|';
$sa = $a->__toString(); $sb = $b->__toString(); $c->__toString();
echo 'W|', (int)($sa===$sb), ':', $a<=>$b, '|';
$source[1] = 99; $left->data[1] = 4; echo 'M|', $source[1], ':', $a<=>$b, ':', $b<=>$a, '|';
$left->data = [1,3]; echo 'E|', $a<=>$b, ':', $a<=>$c, '|';
echo 'A|', [0,$a,1]<=>[0,$c,3], ':', [0,$a,new Tail146]<=>[0,$b,'x'], '|';
''',
    'array-cell-retarget': br'''<?php
function child146($x): TypeError { return new TypeError('inner', 7); }
$live = [1,2]; $snapshot = [1,2]; $payload = [&$live,$snapshot];
$p = child146($payload); $q = child146([[1,3],[1,2]]);
$a = new RuntimeException('same',7,$p); $b = new RuntimeException('same',7,$q);
echo 'B|', $a<=>$b, ':', $b<=>$a, '|';
$snapshot[1] = 99; $live[1] = 4; echo 'M|', $snapshot[1], ':', $a<=>$b, ':', $b<=>$a, '|';
$live = [1,3]; echo 'R|', $a<=>$b, ':', (int)($a==$b), '|';
''',
    'object-cell-retarget-inline': br'''<?php
class Plain146 { public int $x = 0; }
function child146($x): TypeError { return new TypeError('inner', 7); }
$live = new Plain146; $other = new Plain146; $live->x = 1; $other->x = 2; $saved = $live;
$left = new stdClass; $right = new stdClass; $left->p =& $live; $right->p = $other;
$p = child146($left); $q = child146($right);
$a = new ErrorException('same',7,9,'f.php',9,$p); $b = new ErrorException('same',7,1,'f.php',9,$q);
echo 'B|', $a<=>$b, '|';
$live->x = 3; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
$live = new Plain146; $live->x = 2; echo 'R|', $saved->x, ':', $a<=>$b, ':', $b<=>$a, '|';
''',
    'trace-before-link-and-severity': br'''<?php
function child146($x): ErrorException { global $leaf,$severity; return new ErrorException('inner',7,$severity,'i.php',5,$leaf); }
$deep9 = new Error('deep',9); $deep1 = new Error('deep',1);
$left = new stdClass; $right = new stdClass; $left->x = 1; $right->x = 2;
$leaf = $deep9; $severity = 1; $p = child146($left); $leaf = $deep1; $severity = 9; $q = child146($right);
$a = new ErrorException('same',7,1,'f.php',9,$p); $b = new ErrorException('same',7,9,'f.php',9,$q);
echo 'B|', $a<=>$b, ':', $b<=>$a, '|';
$sa = $a->__toString(); $sb = $b->__toString(); echo 'W|', (int)($sa===$sb), ':', $a<=>$b, '|';
$left->x = 2; echo 'P|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'root-trace-graph': br'''<?php
function root146($x): RuntimeException { global $previous; return new RuntimeException('same',7,$previous); }
$previous = new TypeError('inner',7); $left = new stdClass; $right = new stdClass; $left->x = 1; $right->x = 2;
$a = root146($left); $b = root146($right);
echo 'B|', $a<=>$b, ':', $b<=>$a, '|';
$sa = $a->__toString(); $sb = $b->__toString(); echo 'W|', (int)($sa===$sb), ':', $a<=>$b, '|';
$left->x = 3; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'different-captured-classes-control': br'''<?php
class Left146 { public int $x = 1; }
class Right146 { public int $x = 1; }
function child146($x): TypeError { return new TypeError('inner',7); }
$p = child146(new Left146); $q = child146(new Right146);
$a = new RuntimeException('same',7,$p); $b = new RuntimeException('same',7,$q);
echo 'B|', $a<=>$b, '|';
''',
    'object-scalar-control': br'''<?php
function child146($x): TypeError { return new TypeError('inner',7); }
$left = new stdClass; $left->x = 1;
$p = child146($left); $q = child146(1);
$a = new RuntimeException('same',7,$p); $b = new RuntimeException('same',7,$q);
echo 'B|', $a<=>$b, '|';
''',
    'callback-class-control': br'''<?php
class Callback146 { public int $x = 1; public function __toString(): string { echo 'BAD|'; return 'x'; } }
function child146($x): TypeError { return new TypeError('inner',7); }
$p = child146(new Callback146); $q = child146(new Callback146);
$a = new RuntimeException('same',7,$p); $b = new RuntimeException('same',7,$q);
echo 'B|', $a<=>$b, '|';
''',
    'cell-cycle-control': br'''<?php
function child146($x): TypeError { return new TypeError('inner',7); }
$left = new stdClass; $right = new stdClass; $lv = $left; $rv = $right; $left->p =& $lv; $right->p =& $rv;
$p = child146($left); $q = child146($right);
$a = new RuntimeException('same',7,$p); $b = new RuntimeException('same',7,$q);
echo 'B|'; try { echo $a<=>$b, '|'; } catch (Error $error) { echo 'E|', $error->getMessage(), '|'; }
''',
}
