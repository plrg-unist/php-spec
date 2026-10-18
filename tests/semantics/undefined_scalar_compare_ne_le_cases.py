"""Distinct direct-CV !=/<= warnings in both operand orientations."""

CASES = {
    'ne-missing-left': b'''<?php
function scalarNotEqual93($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['x'] = 9;
    $GLOBALS['right'] = 0;
    return true;
}
$right = 2;
set_error_handler('scalarNotEqual93');
$result = $x != $right;
echo 'R:', ($result === false), ':', ($x === 9), ':', ($right === 0), ';END;';
''',
    'ne-missing-right': b'''<?php
function scalarRightNotEqual93($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['x'] = 9;
    $GLOBALS['left'] = 0;
    return true;
}
$left = 2;
set_error_handler('scalarRightNotEqual93');
$result = $left != $x;
echo 'R:', ($result === false), ':', ($x === 9), ':', ($left === 0), ';END;';
''',
    'le-missing-left': b'''<?php
function scalarLeftLessEqual93($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['x'] = 9;
    $GLOBALS['right'] = '0';
    return true;
}
$right = 0;
set_error_handler('scalarLeftLessEqual93');
$result = $x <= $right;
echo 'R:', ($result === true), ':', ($x === 9), ':', ($right === '0'), ';END;';
''',
    'le-missing-right-false': b'''<?php
function scalarRightFalse93($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ';';
    $GLOBALS['x'] = 9; $GLOBALS['left'] = '0'; return false;
}
$left = 0;
set_error_handler('scalarRightFalse93');
$result = ($left <= $x);
echo 'R:', ($result === false), ':', ($left === '0'), ':', ($x === 9), ';END;';
''',
    'ne-throw': b'''<?php
function scalarNotEqualThrow93($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ';';
    $GLOBALS['x'] = 9; $GLOBALS['right'] = false; throw $GLOBALS['chosen'];
}
$right = 1; $result = 41; $chosen = new Exception('selected');
set_error_handler('scalarNotEqualThrow93');
try { $result = ($x != $right); echo 'BAD;'; }
catch (Exception $caught) { echo 'C:', ($caught === $chosen), ':', ($result === 41), ':', ($right === false), ':', ($x === 9), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
    'ne-right-array-boundary': b'''<?php
function scalarNotEqualArray93($n, $m, $file, $line) {
    echo 'H|'; $GLOBALS['x'] = 9; $GLOBALS['right'] = []; return true;
}
$right = 1;
set_error_handler('scalarNotEqualArray93');
echo 'B|'; $result = ($x != $right); echo $result;
''',
}
