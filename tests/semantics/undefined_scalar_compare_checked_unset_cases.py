"""Forward comparisons consume a removed checked left against frozen right NULL."""

CASES = {
    'checked-equal-left-unset': b'''<?php
$left = 2; $calls = 0;
function checkedUnset106($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    unset($GLOBALS['left']); $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('checkedUnset106');
$result = $left == $missing;
echo 'R:', $result === true, ':', !isset($left), ':', $missing === 9, ':', $calls === 1, ';END;';
''',
    'checked-lessequal-reference-unset': b'''<?php
$left = 2; $alias =& $left; $calls = 0;
function checkedUnset106($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    unset($GLOBALS['left']); $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('checkedUnset106');
$result = $left <= $missing;
echo 'R:', $result === true, ':', !isset($left), ':', $missing === 9, ':', $alias === 2, ':', $calls === 1, ';';
$alias = 3;
echo 'A:', $alias === 3, ':', !isset($left), ':', $result === true, ';END;';
''',
    'checked-notequal-unset-no-init': b'''<?php
$left = true; $calls = 0;
function checkedUnset106($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    unset($GLOBALS['left']);
    return true;
}
set_error_handler('checkedUnset106');
$result = $left != $missing;
echo 'R:', $result === false, ':', !isset($left), ':', !isset($missing), ':', $calls === 1, ';END;';
''',
    'checked-less-unset-false': b'''<?php
$left = 1.5; $calls = 0;
function checkedUnset106($level, $message, $file, $line) {
    global $calls; $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    unset($GLOBALS['left']); $GLOBALS['missing'] = 9;
    return false;
}
set_error_handler('checkedUnset106');
$result = $left < $missing;
echo 'R:', $result === false, ':', !isset($left), ':', $missing === 9, ':', $calls === 1, ';END;';
''',
    'checked-equal-array-boundary': b'''<?php
function checkedUnsetArray106($level, $message, $file, $line) {
    echo 'H|'; $GLOBALS['left'] = []; $GLOBALS['missing'] = 9; return true;
}
$left = 2;
set_error_handler('checkedUnsetArray106');
echo 'B|'; $result = $left == $missing; echo $result;
''',
    'checked-greater-checked-right-boundary': b'''<?php
function checkedUnsetGreater106($level, $message, $file, $line) {
    echo 'H|'; unset($GLOBALS['right']); $GLOBALS['missing'] = 9; return true;
}
$right = 2;
set_error_handler('checkedUnsetGreater106');
echo 'B|'; $result = $missing > $right; echo $result === false;
''',
}
