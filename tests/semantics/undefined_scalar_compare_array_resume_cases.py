"""Boolean comparisons consume handler-created flat arrays against frozen NULL."""

CASES = {
    'boolean-array-equal-empty': b'''<?php
$right = '0'; $calls = 0;
function booleanArray109($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['missing'] = 9; $GLOBALS['right'] = [];
    return true;
}
set_error_handler('booleanArray109');
$result = $missing == $right;
echo 'R:', $result === true, ':', $right === [], ':', $missing === 9, ':', $calls === 1, ';';
$right[] = 7; echo 'A:', $right[0] === 7, ':', $result === true, ';END;';
''',
    'boolean-array-greater-nonempty': b'''<?php
$left = 0; $calls = 0;
function booleanArray109($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['left'] = [false]; $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('booleanArray109');
$result = $left > $missing;
echo 'R:', $result === true, ':', $left[0] === false, ':', $missing === 9, ':', $calls === 1, ';';
$left[0] = 7; echo 'A:', $left[0] === 7, ':', $result === true, ';END;';
''',
    'boolean-array-not-equal-nonempty': b'''<?php
$right = 0; $calls = 0;
function notEqualArray109($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['right'] = [false];
    return true;
}
set_error_handler('notEqualArray109');
$result = $missing != $right;
echo 'R:', $result === true, ':', $right[0] === false, ':', !isset($missing), ':', $calls === 1, ';END;';
''',
    'boolean-array-less-empty': b'''<?php
$right = 2; $calls = 0;
function lessArray109($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['right'] = []; $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('lessArray109');
$result = $missing < $right;
echo 'R:', $result === false, ':', $right === [], ':', $missing === 9, ':', $calls === 1, ';END;';
''',
    'boolean-array-less-equal-primitive-tags': b'''<?php
$left = 0; $calls = 0;
function lessEqualArray109($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['left'] = [null, false, 7, 1.5, 'text'];
    return true;
}
set_error_handler('lessEqualArray109');
$result = $left <= $missing;
echo 'R:', $result === false, ':', $left[0] === null, ':', $left[1] === false, ':', $left[2] === 7, ':', $left[3] === 1.5, ':', $left[4] === 'text', ':', !isset($missing), ':', $calls === 1, ';END;';
''',
    'boolean-array-greater-equal-empty': b'''<?php
$right = 1; $calls = 0;
function greaterEqualArray109($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['right'] = []; $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('greaterEqualArray109');
$result = $missing >= $right;
echo 'R:', $result === true, ':', $right === [], ':', $missing === 9, ':', $calls === 1, ';END;';
''',
    'boolean-array-initial-array-boundary': b'''<?php
function initialArray109($level, $message, $file, $line) {
    echo 'H|'; $GLOBALS['right'] = []; $GLOBALS['missing'] = 9; return true;
}
$right = [false];
set_error_handler('initialArray109');
echo 'B|'; $result = $missing == $right; echo $result;
''',
    'boolean-array-nested-array-boundary': b'''<?php
function nestedArray109($level, $message, $file, $line) {
    echo 'H|'; $GLOBALS['left'] = [[false]]; $GLOBALS['missing'] = 9; return true;
}
$left = 0;
set_error_handler('nestedArray109');
echo 'B|'; $result = $left > $missing; echo $result;
''',
}
