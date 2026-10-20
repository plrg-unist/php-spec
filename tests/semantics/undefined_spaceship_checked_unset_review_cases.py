"""Independent checked-left disappearance and unread-right controls."""

CASES = {
    'peer-checked-left-unset-multiline': b'''<?php
$left = '0';
$calls = 0;
function comp105_plain($level, $message, $file, $line) {
    global $left, $missing, $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    unset($GLOBALS['left']);
    $missing = 9;
    return true;
}
set_error_handler('comp105_plain');
$result = (
    $left
    <=> $missing
);
echo 'R:', $result === 0, ':', !isset($left), ':', $missing === 9, ':', $calls === 1, ';END;';
''',
    'peer-checked-reference-unset-default': b'''<?php
$target = '0';
$left =& $target;
$calls = 0;
function comp105_reference($level, $message, $file, $line) {
    global $left, $target, $missing, $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    unset($GLOBALS['left']);
    $target = 8;
    $missing = 9;
    return false;
}
set_error_handler('comp105_reference');
$result = $left <=> $missing;
echo 'R:', $result === 0, ':', !isset($left), ':', $target === 8, ':', $missing === 9, ':', $calls === 1, ';';
$left =& $target;
$left = 6;
echo 'A:', $target === 6, ':', $result === 0, ';END;';
''',
    'peer-unchecked-right-unset-second-warning': b'''<?php
$right = '0';
$calls = 0;
function comp105_unchecked($level, $message, $file, $line) {
    global $left, $right, $calls;
    $calls = $calls + 1;
    echo 'H:', $message === 'Undefined variable $left', ':', $message === 'Undefined variable $right', ':', $line, ':', $calls, ';';
    unset($GLOBALS['right']);
    $left = 9;
    return true;
}
set_error_handler('comp105_unchecked');
$result = $left <=> $right;
echo 'R:', $result === 0, ':', $left === 9, ':', !isset($right), ':', $calls === 2, ';END;';
''',
    'peer-checked-left-unset-supplied-throw': b'''<?php
$left = '0';
$chosen = new Exception('comp105');
$result = 41;
$calls = 0;
function comp105_throw($level, $message, $file, $line) {
    global $left, $chosen, $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    unset($GLOBALS['left']);
    throw $chosen;
}
set_error_handler('comp105_throw');
try {
    $result = $left <=> $missing;
} catch (Exception $caught) {
    echo 'C:', $caught === $chosen, ':', $result === 41, ':', !isset($left), ':', !isset($missing), ':', $calls === 1, ';';
} finally {
    echo 'F;';
}
echo 'END;';
''',
}
