"""A checked left CV removed during the missing-right spaceship Warning."""

CASES = {
    'checked-left-unset-plain': b'''<?php
$left = 2; $calls = 0;
function checkedUnset105($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    unset($GLOBALS['left']); $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('checkedUnset105');
$result = $left <=> $missing;
echo 'R:', $result === 0, ':', !isset($left), ':', $missing === 9, ':', $calls === 1, ';END;';
''',
    'checked-left-unset-reference': b'''<?php
$left = 2; $alias =& $left; $calls = 0;
function checkedUnset105($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    unset($GLOBALS['left']); $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('checkedUnset105');
$result = $left <=> $missing;
echo 'R:', $result === 0, ':', !isset($left), ':', $missing === 9, ':', $alias === 2, ':', $calls === 1, ';';
$alias = 3;
echo 'A:', $alias === 3, ':', !isset($left), ':', $result === 0, ';END;';
''',
    'checked-left-unset-no-init': b'''<?php
$left = true; $calls = 0;
function checkedUnset105($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    unset($GLOBALS['left']);
    return true;
}
set_error_handler('checkedUnset105');
$result = $left <=> $missing;
echo 'R:', $result === 0, ':', !isset($left), ':', !isset($missing), ':', $calls === 1, ';END;';
''',
    'checked-left-unset-false': b'''<?php
$left = 1.5; $calls = 0;
function checkedUnset105($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    unset($GLOBALS['left']); $GLOBALS['missing'] = 9;
    return false;
}
set_error_handler('checkedUnset105');
$result = $left <=> $missing;
echo 'R:', $result === 0, ':', !isset($left), ':', $missing === 9, ':', $calls === 1, ';END;';
''',
    'checked-left-array-boundary': b'''<?php
function checkedUnsetArray105($level, $message, $file, $line) {
    echo 'H|'; $GLOBALS['left'] = []; $GLOBALS['missing'] = 9; return true;
}
$left = 2;
set_error_handler('checkedUnsetArray105');
echo 'B|'; $result = $left <=> $missing; echo $result;
''',
    'checked-left-equal-boundary': b'''<?php
function checkedUnsetEqual105($level, $message, $file, $line) {
    echo 'H|'; unset($GLOBALS['left']); $GLOBALS['missing'] = 9; return true;
}
$left = 2;
set_error_handler('checkedUnsetEqual105');
echo 'B|'; $result = $left == $missing; echo $result;
''',
}
