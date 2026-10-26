"""Frozen native-first recursive standard-object values in Throwable traces."""

CASES = {
    'equal-distinct-child': br'''<?php
function ex140($x): Exception { return new Exception('same', 7); }
$left = new stdClass; $right = new stdClass; $lc = new stdClass; $rc = new stdClass; $lc->x = 1; $rc->x = 1; $left->child = $lc; $right->child = $rc; $a = ex140($left); $b = ex140($right);
echo 'B|', $a<=>$b, ':', (int)($a==$b), ':', (int)($a===$b), '|';
''',
    'live-child-value': br'''<?php
function ex140($x): Exception { return new Exception('same', 7); }
$left = new stdClass; $right = new stdClass; $lc = new stdClass; $rc = new stdClass; $lc->x = 1; $rc->x = 2; $left->child = $lc; $right->child = $rc; $a = ex140($left); $b = ex140($right);
echo 'B|', $a<=>$b, '|';
$lc->x = 3; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
$rc->x = 3; echo 'E|', $a<=>$b, '|';
''',
    'child-count-key': br'''<?php
function ex140($x): Exception { return new Exception('same', 7); }
$left = new stdClass; $right = new stdClass; $lc = new stdClass; $rc = new stdClass; $lc->x = 1; $rc->x = 1; $rc->y = 2; $left->child = $lc; $right->child = $rc; $a = ex140($left); $b = ex140($right);
echo 'C|', $a<=>$b, ':', $b<=>$a, '|';
$x = new stdClass; $y = new stdClass; $xc = new stdClass; $yc = new stdClass; $xc->x = 1; $yc->y = 1; $x->child = $xc; $y->child = $yc; $c = ex140($x); $d = ex140($y);
echo 'K|', $c<=>$d, ':', $d<=>$c, '|';
''',
    'plain-declared-child': br'''<?php
class Plain140 { public int $first = 1; public int $second = 0; }
function ex140($x): Exception { return new Exception('same', 7); }
$left = new stdClass; $right = new stdClass; $lc = new Plain140; $rc = new Plain140; $lc->second = 1; $rc->second = 2; $left->child = $lc; $right->child = $rc; $a = ex140($left); $b = ex140($right);
echo 'B|', $a<=>$b, '|';
$lc->second = 3; echo 'S|', $a<=>$b, '|';
$lc->first = 0; echo 'F|', $a<=>$b, '|';
''',
    'array-child-cow': br'''<?php
function ex140($x): Exception { return new Exception('same', 7); }
$source = [1, 2]; $left = new stdClass; $right = new stdClass; $lc = new stdClass; $rc = new stdClass; $lc->payload = $source; $rc->payload = [1, 3]; $left->child = $lc; $right->child = $rc; $a = ex140($left); $b = ex140($right);
echo 'B|', $a<=>$b, '|';
$source[1] = 9; echo 'C|', $source[1], ':', $lc->payload[1], ':', $a<=>$b, '|';
$lc->payload[1] = 4; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'array-object-descendant': br'''<?php
class Plain140 { public int $x = 0; }
function ex140($x): Exception { return new Exception('same', 7); }
$left = new stdClass; $right = new stdClass; $lc = new stdClass; $rc = new stdClass; $lp = new Plain140; $rp = new Plain140; $lp->x = 1; $rp->x = 2; $lc->payload = [0, $lp]; $rc->payload = [0, $rp]; $left->child = $lc; $right->child = $rc; $a = ex140($left); $b = ex140($right);
echo 'B|', $a<=>$b, '|';
$lp->x = 3; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'array-property-object-only': br'''<?php
class ArrayLeaf140 { public int $x = 0; }
function ex140($x): Exception { return new Exception('same', 7); }
$left = new stdClass; $right = new stdClass; $lc = new ArrayLeaf140; $rc = new ArrayLeaf140; $lc->x = 1; $rc->x = 2; $left->payload = [0, $lc]; $right->payload = [0, $rc]; $a = ex140($left); $b = ex140($right);
echo 'B|', $a<=>$b, '|';
$lc->x = 3; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'shared-child-dag': br'''<?php
function ex140($x): Exception { return new Exception('same', 7); }
$left = new stdClass; $right = new stdClass; $lc = new stdClass; $rc = new stdClass; $lc->x = 1; $rc->x = 1; $left->first = $lc; $left->second = $lc; $right->first = $rc; $right->second = $rc; $a = ex140($left); $b = ex140($right);
echo 'B|', $a<=>$b, '|';
$lc->x = 2; $rc->x = 2; echo 'E|', $a<=>$b, '|';
''',
    'seven-operators': br'''<?php
function ex140($x): Exception { return new Exception('same', 7); }
$left = new stdClass; $right = new stdClass; $lc = new stdClass; $rc = new stdClass; $lc->x = 1; $rc->x = 2; $left->child = $lc; $right->child = $rc; $a = ex140($left); $b = ex140($right);
echo 'B|', (int)($a==$b), (int)($a!=$b), (int)($a<$b), (int)($a<=$b), (int)($a>$b), (int)($a>=$b), ':', $a<=>$b, '|';
$lc->x = 2; echo 'E|', (int)($a==$b), (int)($a!=$b), (int)($a<$b), (int)($a<=$b), (int)($a>$b), (int)($a>=$b), ':', $a<=>$b, '|';
''',
    'error-second-argument': br'''<?php
function err140($tag, $x): Error { return new Error('same', 7); }
$left = new stdClass; $right = new stdClass; $lc = new stdClass; $rc = new stdClass; $lc->x = 1; $rc->x = 2; $left->child = $lc; $right->child = $rc; $a = err140(17, $left); $b = err140(17, $right);
echo 'B|', $a<=>$b, '|';
$lc->x = 3; echo 'M|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'aggregate-tail': br'''<?php
class Tail140 { public function __toString(): string { echo 'CAST|'; return 'x'; } }
function ex140($x): Exception { return new Exception('same', 7); }
$left = new stdClass; $right = new stdClass; $lc = new stdClass; $rc = new stdClass; $lc->x = 1; $rc->x = 1; $left->child = $lc; $right->child = $rc; $a = ex140($left); $b = ex140($right); $tail = new Tail140;
echo 'E|', [$a, $tail]<=>[$b, 'x'], '|';
$lc->x = 3; echo 'N|', [$a, $tail]<=>[$b, 'x'], '|';
''',
    'different-child-class-control': br'''<?php
class Left140 { public int $x = 1; }
class Right140 { public int $x = 1; }
function ex140($x): Exception { return new Exception('same', 7); }
$left = new stdClass; $right = new stdClass; $left->child = new Left140; $right->child = new Right140; $a = ex140($left); $b = ex140($right);
echo 'B|', $a<=>$b, '|';
''',
    'object-scalar-property-control': br'''<?php
function ex140($x): Exception { return new Exception('same', 7); }
$left = new stdClass; $right = new stdClass; $child = new stdClass; $child->x = 1; $left->child = $child; $right->child = 1; $a = ex140($left); $b = ex140($right);
echo 'B|', $a<=>$b, '|';
''',
    'reference-property-control': br'''<?php
function ex140($x): Exception { return new Exception('same', 7); }
$left = new stdClass; $right = new stdClass; $lc = new stdClass; $rc = new stdClass; $lc->x = 1; $rc->x = 1; $left->child =& $lc; $right->child = $rc; $a = ex140($left); $b = ex140($right);
echo 'B|', $a<=>$b, '|';
''',
    'cycle-control': br'''<?php
function ex140($x): Exception { return new Exception('same', 7); }
$left = new stdClass; $right = new stdClass; $left->child = $left; $right->child = $right; $a = ex140($left); $b = ex140($right);
echo 'B|'; try { echo $a<=>$b, '|'; } catch (Error $error) { echo 'E|', $error->getMessage(), '|'; }
''',
}
