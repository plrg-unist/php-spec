"""Independent initially owning arrays, current wrappers, aliases and throw."""

CASES = {
    'peer-initial-array-spaceship-rebound-reference': b'''<?php
$target = [];
$right =& $target;
$copy = $right;
$calls = 0;
function comp110_rebound($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['replacement'] = '0';
    $GLOBALS['right'] =& $GLOBALS['replacement'];
    $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('comp110_rebound');
$result = (
    $missing
    <=> $right
);
echo 'R:', $result === -1, ':', $right === '0', ':', $replacement === '0', ':', $target === [], ':', $copy === [], ':', $missing === 9, ':', $calls === 1, ';';
$target[] = 7;
$right = 6;
echo 'A:', $target[0] === 7, ':', $copy === [], ':', $replacement === 6, ':', $result === -1, ';END;';
''',
    'peer-initial-array-checked-left-unset-default': b'''<?php
$target = [false];
$left =& $target;
$copy = $left;
$calls = 0;
function comp110_checked($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    unset($GLOBALS['left']);
    $GLOBALS['missing'] = 9;
    return false;
}
set_error_handler('comp110_checked');
$result = $left == $missing;
echo 'R:', $result === true, ':', !isset($left), ':', $target[0] === false, ':', $copy[0] === false, ':', $missing === 9, ':', $calls === 1, ';';
$target[0] = 7;
echo 'A:', $target[0] === 7, ':', $copy[0] === false, ':', !isset($left), ';END;';
''',
    'peer-initial-array-unread-forward-and-reversed': b'''<?php
$right = [false];
$right_copy = $right;
$left = [false];
$left_copy = $left;
$calls = 0;
function comp110_unread($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $message === 'Undefined variable $missing', ':', $message === 'Undefined variable $right', ':', $message === 'Undefined variable $later', ':', $message === 'Undefined variable $left', ':', $line, ':', $calls, ';';
    if ($calls === 1) { unset($GLOBALS['right']); $GLOBALS['missing'] = 9; }
    elseif ($calls === 2) { $GLOBALS['right'] = '0'; }
    elseif ($calls === 3) { unset($GLOBALS['left']); $GLOBALS['later'] = 9; }
    else { $GLOBALS['left'] = '0'; }
    return true;
}
set_error_handler('comp110_unread');
$a = $missing < $right;
$b = $left > $later;
echo 'R:', $a === false, ':', $b === false, ':', $right === '0', ':', $left === '0', ':', $right_copy[0] === false, ':', $left_copy[0] === false, ':', $missing === 9, ':', $later === 9, ':', $calls === 4, ';END;';
''',
    'peer-initial-array-first-warning-supplied-throw': b'''<?php
$target = [false];
$left =& $target;
$oldcopy = $left;
$result = 41;
$exception = new Exception('chosen110');
$calls = 0;
function comp110_throw($level, $message, $file, $line) {
    global $calls, $exception;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['left'][0] = 7;
    $GLOBALS['replacement'] = [];
    $GLOBALS['left'] =& $GLOBALS['replacement'];
    $GLOBALS['copy'] = $GLOBALS['left'];
    throw $exception;
}
set_error_handler('comp110_throw');
try {
    $result = $left >= $missing;
} catch (Exception $caught) {
    echo 'C:', $caught === $exception, ':', $result === 41, ':', $left === [], ':', $replacement === [], ':', $copy === [], ':', $target[0] === 7, ':', $oldcopy[0] === false, ':', !isset($missing), ':', $calls === 1, ';';
} finally {
    echo 'F;';
}
$left[] = 8;
echo 'A:', $replacement[0] === 8, ':', $copy === [], ':', $target[0] === 7, ':', $oldcopy[0] === false, ';END;';
''',
}
