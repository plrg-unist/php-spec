"""Captured flat array values across missing spaceship reads."""

CASES = {
    'captured-left-assignment-empty': b'''<?php
$source = [];
$source[] = 4;
unset($source[0]);
$calls = 0;
function capturedAssignmentWarning111($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['source'][] = 7;
    unset($GLOBALS['saved']);
    $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('capturedAssignmentWarning111');
$result = ($saved = $source) <=> $missing;
echo 'R:', $result === 0, ':', $source[1] === 7, ':', !isset($source[0]), ':', !isset($saved), ':', $missing === 9, ':', $calls === 1, ';';
$source[] = 8;
echo 'A:', $source[2] === 8, ':', $source[1] === 7, ':', $result === 0, ';END;';
''',
    'captured-right-runtime-array': b'''<?php
$value = false;
$calls = 0;
function capturedRuntimeWarning111($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['value'] = 7;
    $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('capturedRuntimeWarning111');
$result = $missing <=> [$value];
echo 'R:', $result === -1, ':', $value === 7, ':', $missing === 9, ':', $calls === 1, ';END;';
''',
    'captured-literal-orientations': b'''<?php
$calls = 0;
function capturedLiteralAuthor111($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $line, ':', $calls, ';'; return true;
}
set_error_handler('capturedLiteralAuthor111');
$a = [] <=> $missing;
$b = $missing <=> [false];
echo 'R:', $a === 0, ':', $b === -1, ':', !isset($missing), ':', $calls === 2, ';END;';
''',
    'captured-right-runtime-throw': b'''<?php
$value = false; $result = 41; $calls = 0;
$exception = new Exception('captured111');
function capturedRuntimeThrow111($level, $message, $file, $line) {
    global $calls, $exception; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['value'] = 7; $GLOBALS['missing'] = 9;
    throw $exception;
}
set_error_handler('capturedRuntimeThrow111');
try { $result = $missing <=> [$value]; }
catch (Exception $caught) {
    echo 'C:', $caught === $exception, ':', $result === 41, ':', $value === 7, ':', $missing === 9, ':', $calls === 1, ';';
} finally { echo 'F;'; }
echo 'END;';
''',
    'captured-boolean-boundary': b'''<?php
$value = false;
function capturedBoolean111($level, $message, $file, $line) { echo 'H|'; return true; }
set_error_handler('capturedBoolean111');
echo 'B|'; $result = $missing == [$value]; echo (int)$result;
''',
    'captured-nested-boundary': b'''<?php
function capturedNested111($level, $message, $file, $line) { echo 'H|'; return true; }
set_error_handler('capturedNested111');
echo 'B|'; $result = [[false]] <=> $missing; echo $result;
''',
}
