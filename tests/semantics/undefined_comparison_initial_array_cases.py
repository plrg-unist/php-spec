"""Initially defined direct-CV arrays through missing comparison Warnings."""

CASES = {
    'initial-array-equal-current-empty': b'''<?php
$right = [false]; $calls = 0;
function initialArray110($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['missing'] = 9; $GLOBALS['right'] = [];
    return true;
}
set_error_handler('initialArray110');
$result = $missing == $right;
echo 'R:', $result === true, ':', $right === [], ':', $missing === 9, ':', $calls === 1, ';';
$right[] = 7; echo 'A:', $right[0] === 7, ':', $result === true, ';END;';
''',
    'initial-array-greater-current-string': b'''<?php
$left = []; $calls = 0;
function initialArray110($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['left'] = '0'; $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('initialArray110');
$result = $left > $missing;
echo 'R:', $result === true, ':', $left === '0', ':', $missing === 9, ':', $calls === 1, ';';
$left = 7; echo 'A:', $left === 7, ':', $result === true, ';END;';
''',
    'initial-array-forward-predicates': b'''<?php
$right = []; $calls = 0;
function initialForward110($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    if ($calls === 1) { $GLOBALS['right'] = [false]; }
    elseif ($calls === 2) { $GLOBALS['right'] = []; }
    else { $GLOBALS['left'] = [false]; }
    return true;
}
set_error_handler('initialForward110');
$a = $missing != $right;
$right = [false];
$b = $missing < $right;
$left = [];
$c = $left <= $missing;
echo 'R:', $a === true, ':', $b === false, ':', $c === false, ':', !isset($missing), ':', $calls === 3, ';END;';
''',
    'initial-array-greater-equal-current-empty-default': b'''<?php
$right = [false]; $calls = 0;
function initialGreaterEqual110($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['right'] = []; $GLOBALS['missing'] = 9;
    return false;
}
set_error_handler('initialGreaterEqual110');
$result = $missing >= $right;
echo 'R:', $result === true, ':', $right === [], ':', $missing === 9, ':', $calls === 1, ';END;';
''',
    'initial-array-spaceship-both-orientations': b'''<?php
$right = [false]; $left = []; $calls = 0;
function initialSpace110($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', ($message === 'Undefined variable $missing' || $message === 'Undefined variable $later'), ':', $line, ':', $calls, ';';
    if ($calls === 1) { $GLOBALS['right'] = []; }
    else { $GLOBALS['left'] = [false]; }
    return true;
}
set_error_handler('initialSpace110');
$a = $missing <=> $right;
$b = $left <=> $later;
echo 'R:', $a === 0, ':', $b === 1, ':', $right === [], ':', $left[0] === false, ':', !isset($missing), ':', !isset($later), ':', $calls === 2, ';END;';
''',
    'initial-array-first-warning-throw': b'''<?php
$right = [false]; $copy = $right; $result = 41; $calls = 0;
$exception = new Exception('initial110');
function initialThrow110($level, $message, $file, $line) {
    global $calls, $exception; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['right'][0] = 7; $GLOBALS['right'] = '0';
    throw $exception;
}
set_error_handler('initialThrow110');
try { $result = $missing == $right; }
catch (Exception $caught) {
    echo 'C:', $caught === $exception, ':', $result === 41, ':', $right === '0', ':', $copy[0] === false, ':', !isset($missing), ':', $calls === 1, ';';
} finally { echo 'F;'; }
$copy[0] = 8; echo 'A:', $copy[0] === 8, ':', $right === '0', ':', $result === 41, ';END;';
''',
    'initial-array-captured-boundary': b'''<?php
function capturedArray110($level, $message, $file, $line) {
    echo 'H|'; $GLOBALS['missing'] = 9; return true;
}
set_error_handler('capturedArray110');
echo 'B|'; $result = [] <=> $missing; echo $result;
''',
    'initial-array-nested-boundary': b'''<?php
function nestedInitial110($level, $message, $file, $line) {
    echo 'H|'; $GLOBALS['right'] = []; $GLOBALS['missing'] = 9; return true;
}
$right = [[false]];
set_error_handler('nestedInitial110');
echo 'B|'; $result = $missing == $right; echo $result;
''',
}
