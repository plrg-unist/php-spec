"""Independent callback arrays, live references, COW and abrupt effects."""

CASES = {
    'peer-array-left-missing-fresh-reference-cow': b'''<?php
$right = '0';
$calls = 0;
function comp108_left($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['slot'] = [7];
    $GLOBALS['right'] =& $GLOBALS['slot'];
    $GLOBALS['copy'] = $GLOBALS['right'];
    unset($GLOBALS['slot'][0]);
    $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('comp108_left');
$result = (
    $missing
    <=> $right
);
echo 'R:', $result === 0, ':', $right === [], ':', $slot === [], ':', $copy[0] === 7, ':', $missing === 9, ':', $calls === 1, ';';
$right[] = 6;
echo 'A:', $slot[1] === 6, ':', $copy[0] === 7, ':', $result === 0, ';END;';
''',
    'peer-array-right-missing-rebound-reference-default': b'''<?php
$target = 0;
$left =& $target;
$calls = 0;
function comp108_right($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['replacement'] = [8];
    $GLOBALS['left'] =& $GLOBALS['replacement'];
    $GLOBALS['copy'] = $GLOBALS['left'];
    $GLOBALS['replacement'][0] = 9;
    $GLOBALS['missing'] = 9;
    return false;
}
set_error_handler('comp108_right');
$result = $left <=> $missing;
echo 'R:', $result === 1, ':', $left[0] === 9, ':', $replacement[0] === 9, ':', $copy[0] === 8, ':', $target === 0, ':', $missing === 9, ':', $calls === 1, ';';
$left[0] = 6;
echo 'A:', $replacement[0] === 6, ':', $copy[0] === 8, ':', $target === 0, ';END;';
''',
    'peer-array-callback-both-missing-and-same-name': b'''<?php
$calls = 0;
function comp108_noinit($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $message === 'Undefined variable $missing', ':', $message === 'Undefined variable $x', ':', $line, ':', $calls, ';';
    if ($calls === 1) { $GLOBALS['right'] = [false]; }
    else { $GLOBALS['x'] = []; }
    return true;
}
set_error_handler('comp108_noinit');
$a = $missing <=> $right;
$b = $x <=> $x;
echo 'R:', $a === -1, ':', $b === 0, ':', $right[0] === false, ':', $x === [], ':', !isset($missing), ':', $calls === 2, ';END;';
''',
    'peer-array-callback-supplied-throw': b'''<?php
$left = 0;
$result = 41;
$exception = new Exception('chosen108');
$calls = 0;
function comp108_throw($level, $message, $file, $line) {
    global $calls, $exception;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['left'] = [3];
    $GLOBALS['copy'] = $GLOBALS['left'];
    throw $exception;
}
set_error_handler('comp108_throw');
try {
    $result = $left <=> $missing;
} catch (Exception $caught) {
    echo 'C:', $caught === $exception, ':', $result === 41, ':', $left[0] === 3, ':', $copy[0] === 3, ':', !isset($missing), ':', $calls === 1, ';';
} finally {
    echo 'F;';
}
$left[0] = 4;
echo 'A:', $copy[0] === 3, ':', $left[0] === 4, ';END;';
''',
}
