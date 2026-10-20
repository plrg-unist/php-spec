"""Independent Boolean arrays, current references, COW and abrupt effects."""

CASES = {
    'peer-boolean-array-equal-fresh-reference-cow': b'''<?php
$right = '0';
$calls = 0;
function comp109_equal($level, $message, $file, $line) {
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
set_error_handler('comp109_equal');
$result = (
    $missing
    == $right
);
echo 'R:', $result === true, ':', $right === [], ':', $slot === [], ':', $copy[0] === 7, ':', $missing === 9, ':', $calls === 1, ';';
$right[] = 6;
echo 'A:', $slot[1] === 6, ':', $copy[0] === 7, ':', $result === true, ';END;';
''',
    'peer-boolean-array-greater-rebound-reference-default': b'''<?php
$target = 0;
$left =& $target;
$calls = 0;
function comp109_greater($level, $message, $file, $line) {
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
set_error_handler('comp109_greater');
$result = $left > $missing;
echo 'R:', $result === true, ':', $left[0] === 9, ':', $replacement[0] === 9, ':', $copy[0] === 8, ':', $target === 0, ':', $missing === 9, ':', $calls === 1, ';';
$left[0] = 6;
echo 'A:', $replacement[0] === 6, ':', $copy[0] === 8, ':', $target === 0, ';END;';
''',
    'peer-boolean-array-both-missing-and-same-name': b'''<?php
$calls = 0;
function comp109_missing($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $line, ':', $calls, ';';
    if ($calls === 1) { $GLOBALS['right'] = [false]; }
    elseif ($calls === 2) { $GLOBALS['x'] = [false]; }
    elseif ($calls === 3) { $GLOBALS['y'] = []; }
    else { $GLOBALS['z'] = [false]; }
    return true;
}
set_error_handler('comp109_missing');
$a = $missing < $right;
$b = $x != $x;
$c = $y <= $y;
$d = $z >= $z;
echo 'R:', $a === true, ':', $b === true, ':', $c === true, ':', $d === true, ':', $right[0] === false, ':', $x[0] === false, ':', $y === [], ':', $z[0] === false, ':', !isset($missing), ':', $calls === 4, ';END;';
''',
    'peer-boolean-array-first-warning-supplied-throw': b'''<?php
$target = 0;
$left =& $target;
$result = 41;
$exception = new Exception('chosen109');
$calls = 0;
function comp109_throw($level, $message, $file, $line) {
    global $calls, $exception;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['replacement'] = [3];
    $GLOBALS['left'] =& $GLOBALS['replacement'];
    $GLOBALS['copy'] = $GLOBALS['left'];
    throw $exception;
}
set_error_handler('comp109_throw');
try {
    $result = $left <= $missing;
} catch (Exception $caught) {
    echo 'C:', $caught === $exception, ':', $result === 41, ':', $left[0] === 3, ':', $replacement[0] === 3, ':', $copy[0] === 3, ':', $target === 0, ':', !isset($missing), ':', $calls === 1, ';';
} finally {
    echo 'F;';
}
$left[0] = 4;
echo 'A:', $replacement[0] === 4, ':', $copy[0] === 3, ':', $target === 0, ';END;';
''',
}
