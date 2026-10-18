"""Missing-left direct-CV == and < warning continuations."""

CASES = {
    'equal-live-plain': b'''<?php
function scalarEqual91($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['x'] = 9;
    $GLOBALS['right'] = 0;
    return true;
}
$right = 2;
set_error_handler('scalarEqual91');
$result = $x == $right;
echo 'R:', ($result === true), ':', ($x === 9), ':', ($right === 0), ';END;';
''',
    'less-live-string': b'''<?php
function scalarLess91($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['x'] = 9;
    $GLOBALS['right'] = '0';
    return true;
}
$right = 0;
set_error_handler('scalarLess91');
$result = $x < $right;
echo 'R:', ($result === true), ':', ($x === 9), ':', ($right === '0'), ';END;';
''',
    'scalar-tags-both-operators': b'''<?php
function scalarCompareTags91($n, $m, $file, $line) {
    $GLOBALS['x'] = 9; $GLOBALS['right'] = $GLOBALS['next']; return true;
}
set_error_handler('scalarCompareTags91');
echo 'B|';
$part = 'request'; $right = 1; $next = null; echo ($x == $right) ? 'T' : 'F', ':'; unset($x);
$part = 'request'; $right = 1; $next = null; echo ($x < $right) ? 'T' : 'F', ':'; unset($x);
$part = 'request'; $right = 1; $next = false; echo ($x == $right) ? 'T' : 'F', ':'; unset($x);
$part = 'request'; $right = 1; $next = false; echo ($x < $right) ? 'T' : 'F', ':'; unset($x);
$part = 'request'; $right = 1; $next = true; echo ($x == $right) ? 'T' : 'F', ':'; unset($x);
$part = 'request'; $right = 1; $next = true; echo ($x < $right) ? 'T' : 'F', ':'; unset($x);
$part = 'request'; $right = 1; $next = 0; echo ($x == $right) ? 'T' : 'F', ':'; unset($x);
$part = 'request'; $right = 1; $next = 0; echo ($x < $right) ? 'T' : 'F', ':'; unset($x);
$part = 'request'; $right = 1; $next = 1.5; echo ($x == $right) ? 'T' : 'F', ':'; unset($x);
$part = 'request'; $right = 1; $next = 1.5; echo ($x < $right) ? 'T' : 'F', ':'; unset($x);
$part = 'request'; $right = 1; $next = NAN; echo ($x == $right) ? 'T' : 'F', ':'; unset($x);
$part = 'request'; $right = 1; $next = NAN; echo ($x < $right) ? 'T' : 'F', ':'; unset($x);
$part = 'request'; $right = 1; $next = '0'; echo ($x == $right) ? 'T' : 'F', ':'; unset($x);
$part = 'request'; $right = 1; $next = '0'; echo ($x < $right) ? 'T' : 'F', ':'; unset($x);
$part = 'request'; $right = 1; $next = $part . '0'; echo ($x == $right) ? 'T' : 'F', ':'; unset($x);
$part = 'request'; $right = 1; $next = $part . '0'; echo ($x < $right) ? 'T' : 'F', ':'; unset($x);
echo 'END;';
''',
    'less-false-default': b'''<?php
function scalarCompareFalse91($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ';';
    $GLOBALS['x'] = 9; $GLOBALS['right'] = '0'; return false;
}
$right = 0;
set_error_handler('scalarCompareFalse91');
$result = ($x < $right);
echo 'R:', ($result === true), ':', ($right === '0'), ':', ($x === 9), ';END;';
''',
    'equal-throw': b'''<?php
function scalarCompareThrow91($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ';';
    $GLOBALS['x'] = 9; $GLOBALS['right'] = false; throw $GLOBALS['chosen'];
}
$right = 1; $result = 41; $chosen = new Exception('selected');
set_error_handler('scalarCompareThrow91');
try { $result = ($x == $right); echo 'BAD;'; }
catch (Exception $caught) { echo 'C:', ($caught === $chosen), ':', ($result === 41), ':', ($right === false), ':', ($x === 9), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
    'right-array-boundary': b'''<?php
function scalarCompareArray91($n, $m, $file, $line) {
    echo 'H|'; $GLOBALS['x'] = 9; $GLOBALS['right'] = []; return true;
}
$right = 1;
set_error_handler('scalarCompareArray91');
echo 'B|'; $result = ($x == $right); echo $result;
''',
}
