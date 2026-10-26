"""Canonical Throwable traces with finite DIRECT array argument graphs."""

CASES = {
'nested-values': br'''<?php
function ex131($x): Exception { return new Exception('same', 7); }
$a = ex131([1, ['k'=>2]]); $b = ex131([1, ['k'=>2]]); $c = ex131([1, ['k'=>3]]);
echo 'B|', (int)($a==$b), ':', $a<=>$b, '|';
foreach ([[$a,$c],[$c,$a]] as [$x,$y]) echo (int)($x==$y), (int)($x!=$y), (int)($x<$y), (int)($x<=$y), (int)($x>$y), (int)($x>=$y), ':', $x<=>$y, '|';
''',
'count-and-keys': br'''<?php
function ex131($x): Exception { return new Exception('same', 7); }
$a = ex131([1]); $b = ex131([1,2]); $c = ex131([0=>1]); $d = ex131([1=>1]);
echo 'B|', $a<=>$b, ':', $b<=>$a, '|', $c<=>$d, ':', $d<=>$c, '|', $a<=>$c, '|';
''',
'cow-and-tail': br'''<?php
class Tail131 { public function __toString(): string { echo 'CAST|'; return 'x'; } }
function ex131($x): Exception { return new Exception('same', 7); }
$input = [1, ['k'=>2]]; $a = ex131($input); $input[1]['k'] = 9; $b = ex131([1, ['k'=>2]]); $c = ex131([1, ['k'=>3]]); $later = new Tail131;
echo 'B|', $input[1]['k'], ':', $a<=>$b, '|';
echo 'E:', [$a,$later]<=>[$b,'x'], '|';
echo 'N:', [$a,$later]<=>[$c,'x'], '|';
''',
'error-array': br'''<?php
function err131($flag, $x): Error { return new Error('same', 7); }
$a = err131(null, [1, ['k'=>2]]); $b = err131(null, [1, ['k'=>3]]); $c = err131(null, [1, ['k'=>2]]);
echo 'B|', $a<=>$b, ':', $b<=>$a, ':', $a<=>$c, '|';
''',
'shared-dag': br'''<?php
function ex131($x): Exception { return new Exception('same', 7); }
$child = [1]; $left = [$child,$child]; $right = [$child,$child]; $a = ex131($left); $b = ex131($right);
echo 'B|', $a<=>$b, '|';
''',
'object-control': br'''<?php
function ex131($x): Exception { return new Exception('same', 7); }
$a = ex131([new stdClass]); $b = ex131([new stdClass]);
echo 'B|', $a<=>$b, '|';
''',
'reference-control': br'''<?php
function ex131($x): Exception { return new Exception('same', 7); }
$v = 1; $input = [&$v]; $a = ex131($input); $b = ex131($input);
echo 'B|', $a<=>$b, '|';
''',
'cycle-control': br'''<?php
function ex131($x): Exception { return new Exception('same', 7); }
$left = []; $left['self'] =& $left; $right = []; $right['self'] =& $right; $a = ex131($left); $b = ex131($right);
echo 'B|'; try { echo $a<=>$b; } catch (Error $e) { echo 'ERR:', $e->getMessage(); } echo '|';
''',
}
