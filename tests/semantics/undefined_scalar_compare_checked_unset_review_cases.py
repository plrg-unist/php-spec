"""Independent quiet checked-left Boolean comparisons and aliases."""

CASES = {
    'peer-checked-equal-unset-fresh-alias': b'''<?php
$left = '0';
$calls = 0;
function comp106_equal($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['alias'] =& $GLOBALS['left'];
    unset($GLOBALS['left']);
    $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('comp106_equal');
$result = (
    $left
    == $missing
);
echo 'R:', $result === true, ':', !isset($left), ':', $alias === '0', ':', $missing === 9, ':', $calls === 1, ';';
$alias = 5;
echo 'A:', $alias === 5, ':', !isset($left), ':', $result === true, ';END;';
''',
    'peer-checked-less-unset-target-default': b'''<?php
$target = '0';
$left =& $target;
$calls = 0;
function comp106_less($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    unset($GLOBALS['left']);
    $GLOBALS['target'] = 8;
    $GLOBALS['missing'] = 9;
    return false;
}
set_error_handler('comp106_less');
$result = $left < $missing;
echo 'R:', $result === false, ':', !isset($left), ':', $target === 8, ':', $missing === 9, ':', $calls === 1, ';';
$left =& $target;
$left = 6;
echo 'A:', $target === 6, ':', $result === false, ';END;';
''',
    'peer-checked-notequal-lessequal-unset-no-init': b'''<?php
$left = true;
$calls = 0;
function comp106_noinit($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    unset($GLOBALS['left']);
    return true;
}
set_error_handler('comp106_noinit');
$ne = $left != $missing;
$left = '0';
$le = $left <= $missing;
echo 'R:', $ne === false, ':', $le === true, ':', !isset($left), ':', !isset($missing), ':', $calls === 2, ';END;';
''',
    'peer-checked-equal-unset-supplied-throw': b'''<?php
$left = '0';
$chosen = new Exception('comp106');
$result = 41;
$calls = 0;
function comp106_throw($level, $message, $file, $line) {
    global $chosen, $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    unset($GLOBALS['left']);
    throw $chosen;
}
set_error_handler('comp106_throw');
try {
    $result = $left == $missing;
} catch (Exception $caught) {
    echo 'C:', $caught === $chosen, ':', $result === 41, ':', !isset($left), ':', !isset($missing), ':', $calls === 1, ';';
} finally {
    echo 'F;';
}
echo 'END;';
''',
}
