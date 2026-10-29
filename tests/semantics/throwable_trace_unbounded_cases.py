"""Frozen finite captured graphs beyond the former local depth bound."""

CASES = {
    'deep-inline-live-leaf': br'''<?php
class Plain149 { public $next = null; public $value = 0; }
function child149($x): TypeError { return new TypeError('inner', 7); }
$left = new Plain149; $right = new Plain149; $lp = $left; $rp = $right;
for ($i = 0; $i < 24; $i++) { $lp->next = new Plain149; $rp->next = new Plain149; $lp = $lp->next; $rp = $rp->next; }
$lp->value = 1; $rp->value = 2;
$p = child149($left); $q = child149($right);
$a = new ErrorException('root', 7, 9, __FILE__, 20, $p); $b = new ErrorException('root', 7, 1, __FILE__, 20, $q);
echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';
$lp->value = 3; echo 'M|', $a <=> $b, ':', $b <=> $a, '|';
$lp->value = 2; echo 'E|', $a <=> $b, '|';
''',
    'deep-cycle-before-count-and-identity': br'''<?php
function child149($x): TypeError { return new TypeError('inner', 7); }
$left = new stdClass; $right = new stdClass; $lp = $left; $rp = $right;
for ($i = 0; $i < 24; $i++) { $lp->next = new stdClass; $rp->next = new stdClass; $lp = $lp->next; $rp = $rp->next; }
$other = new stdClass; $other->next = 0; $other->extra = 0; $lp->next = $left; $rp->next = $other;
$p = child149($left); $q = child149($right);
$a = new ErrorException('root', 7, 9, __FILE__, 20, $p); $b = new ErrorException('root', 7, 1, __FILE__, 20, $q);
$sa = (string)$a; $sb = (string)$b; echo 'B|', (int)($sa === $sb), ':';
try { echo $a <=> $b; } catch (Error $e) { echo 'E|', $e->getMessage(), '|'; }
$rp->next = $left; echo 'I|', $a <=> $b, '|';
''',
    'deep-shared-dag-and-tail-skip': br'''<?php
class Tail149 { public function __toString() { echo 'BAD|'; return 'x'; } }
function child149($x): TypeError { return new TypeError('inner', 7); }
$lc = new stdClass; $rc = new stdClass; $lp = $lc; $rp = $rc;
for ($i = 0; $i < 24; $i++) { $lp->next = new stdClass; $rp->next = new stdClass; $lp = $lp->next; $rp = $rp->next; }
$lp->value = 1; $rp->value = 1;
$left = new stdClass; $right = new stdClass; $left->first = $lc; $left->second = $lc; $right->first = $rc; $right->second = $rc;
$p = child149($left); $q = child149($right);
$a = new RuntimeException('root', 7, $p); $b = new RuntimeException('root', 7, $q);
echo 'B|', $a <=> $b, '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';
$lp->value = 2; echo 'M|', $a <=> $b, ':', $b <=> $a, '|';
echo 'A|', [0, $a, new Tail149] <=> [0, $b, 'x'], '|';
''',
}

# Each level retains a distinct live cell, rather than retargeting a single cell
# in a construction loop and accidentally producing a cycle.
_cell_lines = ["<?php", "function child149($x): TypeError { return new TypeError('inner', 7); }",
               "$left0 = 1; $right0 = 2;"]
for _level in range(1, 25):
    _cell_lines.append(f'$left{_level} = [&$left{_level - 1}]; $right{_level} = [&$right{_level - 1}];')
_cell_lines += [
    "$p = child149($left24); $q = child149($right24);",
    "$a = new ErrorException('root', 7, 9, __FILE__, 20, $p); $b = new ErrorException('root', 7, 1, __FILE__, 20, $q);",
    "echo 'B|', $a <=> $b, ':', $b <=> $a, '|';",
    "$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';",
    "$left0 = 3; echo 'M|', $a <=> $b, ':', $b <=> $a, '|';",
    "$left12 = [1]; $right12 = [9]; $left0 = 99; echo 'R|', $a <=> $b, '|';",
]
CASES['deep-cell-array-retarget'] = ('\n'.join(_cell_lines) + '\n').encode()
del _cell_lines, _level
