"""Both-missing greater comparisons with physical source-right Warning first."""

CASES = {
    'gt-both-init': b'''<?php
function scalarBothGreater96($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['x'] = 9;
    $GLOBALS['left'] = '0';
    return true;
}
$result = 41;
set_error_handler('scalarBothGreater96');
$result = $left > $x;
echo 'R:', ($result === true), ':', ($x === 9), ':', ($left === '0'), ';END;';
''',
    'ge-both-init': b'''<?php
function scalarBothGreaterEqual96($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['x'] = 9;
    $GLOBALS['left'] = 0;
    return true;
}
$result = 41;
set_error_handler('scalarBothGreaterEqual96');
$result = $left >= $x;
echo 'R:', ($result === true), ':', ($x === 9), ':', ($left === 0), ';END;';
''',
    'gt-both-false': b'''<?php
function scalarBothFalse96($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ';';
    $GLOBALS['x'] = 9; $GLOBALS['left'] = '0'; return false;
}
$result = 41;
set_error_handler('scalarBothFalse96');
$result = ($left > $x);
echo 'R:', ($result === true), ':', ($left === '0'), ':', ($x === 9), ';END;';
''',
    'ge-both-no-init-right': b'''<?php
function scalarBothNoInit96($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['left'] = 0;
    return true;
}
$result = 41;
set_error_handler('scalarBothNoInit96');
$result = ($left >= $x);
echo 'R:', ($result === true), ':', ($left === 0), ':', !isset($x), ';END;';
''',
    'gt-both-throw': b'''<?php
function scalarBothThrow96($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ';';
    throw $GLOBALS['chosen'];
}
$result = 41; $chosen = new Exception('selected');
set_error_handler('scalarBothThrow96');
try { $result = ($left > $x); echo 'BAD;'; }
catch (Exception $caught) { echo 'C:', ($caught === $chosen), ':', ($result === 41), ':', !isset($left), ':', !isset($x), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
    'gt-both-array-boundary': b'''<?php
function scalarBothArray96($n, $m, $file, $line) {
    echo 'H|'; $GLOBALS['x'] = 9; $GLOBALS['left'] = []; return true;
}
$result = 41;
set_error_handler('scalarBothArray96');
echo 'B|'; $result = ($left > $x); echo $result;
''',
}
