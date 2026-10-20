"""Reversed comparisons quietly consume a removed already checked right CV."""

CASES = {
    'greater-checked-right-unset': br'''<?php
$right = '0'; $calls = 0;
function checkedRightUnset107($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    unset($GLOBALS['right']); $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('checkedRightUnset107');
$result = $missing > $right;
echo 'R:', $result === false, ':', !isset($right), ':', $missing === 9, ':', $calls === 1, ';END;';
''',
    'greater-equal-checked-reference-unset': br'''<?php
$right = '0'; $alias =& $right; $calls = 0;
function checkedRightUnset107($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    unset($GLOBALS['right']); $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('checkedRightUnset107');
$result = $missing >= $right;
echo 'R:', $result === true, ':', !isset($right), ':', $missing === 9, ':', $alias === '0', ':', $calls === 1, ';';
$alias = 5;
echo 'A:', $alias === 5, ':', !isset($right), ':', $result === true, ';END;';
''',
    'greater-checked-right-no-init': br'''<?php
$right = true; $calls = 0;
function checkedRightUnset107($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    unset($GLOBALS['right']);
    return true;
}
set_error_handler('checkedRightUnset107');
$result = $missing > $right;
echo 'R:', $result === false, ':', !isset($right), ':', !isset($missing), ':', $calls === 1, ';END;';
''',
    'greater-equal-checked-right-false': br'''<?php
$right = 1.5; $calls = 0;
function checkedRightUnset107($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    unset($GLOBALS['right']); $GLOBALS['missing'] = 9;
    return false;
}
set_error_handler('checkedRightUnset107');
$result = $missing >= $right;
echo 'R:', $result === true, ':', !isset($right), ':', $missing === 9, ':', $calls === 1, ';END;';
''',
    'unchecked-left-still-warns-again': br'''<?php
$left = 2; $calls = 0;
function uncheckedLeft107($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $message === 'Undefined variable $missing', ':', $message === 'Undefined variable $left', ':', $line, ':', $calls, ';';
    unset($GLOBALS['left']); $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('uncheckedLeft107');
$result = $left > $missing;
echo 'R:', $result === false, ':', !isset($left), ':', $missing === 9, ':', $calls === 2, ';END;';
''',
    'greater-checked-right-array-boundary': br'''<?php
$right = 2;
function changedRightArray107($level, $message, $file, $line) {
    $GLOBALS['right'] = []; $GLOBALS['missing'] = 9;
    echo 'H|'; return true;
}
set_error_handler('changedRightArray107');
echo 'B|'; $result = $missing > $right;
echo $result === false;
''',
}
