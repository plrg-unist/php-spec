"""Captured flat array snapshots at Boolean comparison Warning reads."""

CASES = {
    'captured-equal-right-empty': b'''<?php
$source = [];
$source[] = 4;
unset($source[0]);
$calls = 0;
function capturedEqualWarning112($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['source'][] = 7;
    unset($GLOBALS['saved']);
    $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('capturedEqualWarning112');
$result = $missing == ($saved = $source);
echo 'R:', $result === true, ':', $source[1] === 7, ':', !isset($source[0]), ':', !isset($saved), ':', $missing === 9, ':', $calls === 1, ';';
$source[] = 8;
echo 'A:', $source[2] === 8, ':', $source[1] === 7, ':', $result === true, ';END;';
''',
    'captured-greater-left-runtime': b'''<?php
$value = false;
$calls = 0;
function capturedGreaterWarning112($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['value'] = 7;
    $GLOBALS['saved'] = [];
    $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('capturedGreaterWarning112');
$result = ($saved = [$value]) > $missing;
echo 'R:', $result === true, ':', $value === 7, ':', $saved === [], ':', $missing === 9, ':', $calls === 1, ';END;';
''',
    'captured-forward-predicates': b'''<?php
$empty = []; $calls = 0;
function capturedForward112($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $line, ':', $calls, ';';
    $GLOBALS['savedA'] = [false]; $GLOBALS['savedB'] = [false];
    return true;
}
set_error_handler('capturedForward112');
$a = $missing != ($savedA = $empty);
$b = $missing < ($savedB = $empty);
echo 'R:', $a === false, ':', $b === false, ':', !isset($missing), ':', $savedA[0] === false, ':', $savedB[0] === false, ':', $calls === 2, ';END;';
''',
    'captured-less-equal-default': b'''<?php
$calls = 0;
function capturedLessEqual112($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['saved'] = []; $GLOBALS['missing'] = 9;
    return false;
}
set_error_handler('capturedLessEqual112');
$result = ($saved = [false]) <= $missing;
echo 'R:', $result === false, ':', $saved === [], ':', $missing === 9, ':', $calls === 1, ';END;';
''',
    'captured-greater-equal-empty': b'''<?php
$calls = 0;
function capturedGreaterEqual112($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['missing'] = 9; return true;
}
set_error_handler('capturedGreaterEqual112');
$result = $missing >= [];
echo 'R:', $result === true, ':', $missing === 9, ':', $calls === 1, ';END;';
''',
    'captured-not-equal-runtime-throw': b'''<?php
$value = false; $result = 41; $calls = 0;
$exception = new Exception('captured112');
function capturedNotEqualThrow112($level, $message, $file, $line) {
    global $calls, $exception; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['value'] = 7; $GLOBALS['missing'] = 9;
    throw $exception;
}
set_error_handler('capturedNotEqualThrow112');
try { $result = $missing != [$value]; }
catch (Exception $caught) {
    echo 'C:', $caught === $exception, ':', $result === 41, ':', $value === 7, ':', $missing === 9, ':', $calls === 1, ';';
} finally { echo 'F;'; }
echo 'END;';
''',
    'captured-primitive-boundary': b'''<?php
function capturedPrimitive112($level, $message, $file, $line) { echo 'H|'; return true; }
set_error_handler('capturedPrimitive112');
echo 'B|'; $result = 2 == $missing; echo (int)$result;
''',
    'captured-nested-boundary': b'''<?php
function capturedNested112($level, $message, $file, $line) { echo 'H|'; return true; }
set_error_handler('capturedNested112');
echo 'B|'; $result = [[false]] <= $missing; echo (int)$result;
''',
}
