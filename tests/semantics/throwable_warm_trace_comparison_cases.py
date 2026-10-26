"""Warmed builtin Throwable comparisons with canonical nonempty trace graphs."""

CASES = {
    'scalar-cache-order': br'''<?php
function ex133($x): Exception { return new Exception('same', 7); }
$a = ex133(9); $b = ex133(10);
echo 'B|', $a<=>$b, ':'; $a->__toString(); $b->__toString(); echo $a<=>$b, ':', $b<=>$a, '|';
''',
    'array-cache-cow-tail': br'''<?php
class Tail133 { public function __toString(): string { echo 'CAST|'; return 'x'; } }
function ex133($x): Exception { return new Exception('same', 7); }
$source = [1, ['k'=>2]]; $a = ex133($source); $source[1]['k'] = 9; $b = ex133([1, ['k'=>2]]); $c = ex133([1, ['k'=>3]]); $tail = new Tail133;
$a->__toString();
echo 'W|', $a<=>$c, '|';
$b->__toString(); $c->__toString();
echo 'C|', $source[1]['k'], ':', $a<=>$b, ':', $a<=>$c, ':', $c<=>$a, '|';
echo 'E:', [$a,$tail]<=>[$b,'x'], '|';
echo 'N:', [$a,$tail]<=>[$c,'x'], '|';
''',
    'error-array-count-key': br'''<?php
function err133($x): Error { return new Error('same', 7); }
$a = err133([1]); $b = err133([1,2]); $c = err133([1=>1]); $d = err133([0=>1]);
$a->__toString(); $b->__toString(); $c->__toString(); $d->__toString();
echo 'B|', $a<=>$b, ':', $b<=>$a, '|', $c<=>$d, ':', $d<=>$c, '|';
''',
    'empty-nonempty-trace': br'''<?php
function ex133($x): Exception { return new Exception('same', 7); }
$a = new Exception('same', 7); $b = ex133(1); $a->__toString(); $b->__toString();
echo 'B|', $a<=>$b, ':', $b<=>$a, '|';
''',
    'object-arg-control': br'''<?php
function ex133($x): Exception { return new Exception('same', 7); }
$a = ex133(new stdClass); $b = ex133(new stdClass); $a->__toString(); $b->__toString();
echo 'B|', $a<=>$b, '|';
''',
    'reference-arg-control': br'''<?php
function ex133($x): Exception { return new Exception('same', 7); }
$v = 1; $input = [&$v]; $a = ex133($input); $b = ex133($input); $a->__toString(); $b->__toString();
echo 'B|', $a<=>$b, '|';
''',
    'cycle-arg-control': br'''<?php
function ex133($x): Exception { return new Exception('same', 7); }
$left = []; $left['self'] =& $left; $right = []; $right['self'] =& $right; $a = ex133($left); $b = ex133($right); $a->__toString(); $b->__toString();
echo 'B|'; try { echo $a<=>$b; } catch (Error $e) { echo 'ERR:', $e->getMessage(); } echo '|';
''',
    'cold-array-baseline': br'''<?php
function ex133($x): Exception { return new Exception('same', 7); }
$a = ex133([1]); $b = ex133([2]);
echo 'B|', $a<=>$b, '|';
''',
}
