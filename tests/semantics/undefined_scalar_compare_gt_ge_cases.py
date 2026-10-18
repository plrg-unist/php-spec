"""Distinct direct-CV >/>= warnings in both operand orientations."""

CASES = {
    'gt-missing-left': b'''<?php
function scalarGreater94($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['x'] = 9;
    $GLOBALS['right'] = 0;
    return true;
}
$right = 2;
set_error_handler('scalarGreater94');
$result = $x > $right;
echo 'R:', ($result === false), ':', ($x === 9), ':', ($right === 0), ';END;';
''',
    'gt-missing-right': b'''<?php
function scalarRightGreater94($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['x'] = 9;
    $GLOBALS['left'] = '0';
    return true;
}
$left = 0;
set_error_handler('scalarRightGreater94');
$result = $left > $x;
echo 'R:', ($result === true), ':', ($x === 9), ':', ($left === '0'), ';END;';
''',
    'ge-missing-left': b'''<?php
function scalarLeftGreaterEqual94($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['x'] = 9;
    $GLOBALS['right'] = '0';
    return true;
}
$right = 0;
set_error_handler('scalarLeftGreaterEqual94');
$result = $x >= $right;
echo 'R:', ($result === false), ':', ($x === 9), ':', ($right === '0'), ';END;';
''',
    'ge-missing-right-false': b'''<?php
function scalarRightFalse94($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ';';
    $GLOBALS['x'] = 9; $GLOBALS['left'] = '0'; return false;
}
$left = 0;
set_error_handler('scalarRightFalse94');
$result = ($left >= $x);
echo 'R:', ($result === true), ':', ($left === '0'), ':', ($x === 9), ';END;';
''',
    'gt-throw': b'''<?php
function scalarGreaterThrow94($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ';';
    $GLOBALS['x'] = 9; $GLOBALS['right'] = false; throw $GLOBALS['chosen'];
}
$right = 1; $result = 41; $chosen = new Exception('selected');
set_error_handler('scalarGreaterThrow94');
try { $result = ($x > $right); echo 'BAD;'; }
catch (Exception $caught) { echo 'C:', ($caught === $chosen), ':', ($result === 41), ':', ($right === false), ':', ($x === 9), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
    'gt-left-array-boundary': b'''<?php
function scalarGreaterArray94($n, $m, $file, $line) {
    echo 'H|'; $GLOBALS['x'] = 9; $GLOBALS['left'] = []; return true;
}
$left = 1;
set_error_handler('scalarGreaterArray94');
echo 'B|'; $result = ($left > $x); echo $result;
''',
}
