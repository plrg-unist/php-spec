"""Independent originals for reversed checked-right removal."""

CASES = {
    'peer-checked-greaterequal-unset-fresh-alias': b'''<?php
$right = '0';
$calls = 0;
function comp107_ge($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['alias'] =& $GLOBALS['right'];
    unset($GLOBALS['right']);
    $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('comp107_ge');
$result = (
    $missing
    >= $right
);
echo 'R:', $result === true, ':', !isset($right), ':', $alias === '0', ':', $missing === 9, ':', $calls === 1, ';';
$alias = 5;
echo 'A:', $alias === 5, ':', !isset($right), ':', $result === true, ';END;';
''',
    'peer-checked-greater-unset-target-default': b'''<?php
$target = '0';
$right =& $target;
$calls = 0;
function comp107_gt($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    unset($GLOBALS['right']);
    $GLOBALS['target'] = 8;
    $GLOBALS['missing'] = 9;
    return false;
}
set_error_handler('comp107_gt');
$result = $missing > $right;
echo 'R:', $result === false, ':', !isset($right), ':', $target === 8, ':', $missing === 9, ':', $calls === 1, ';';
$right =& $target;
$right = 6;
echo 'A:', $target === 6, ':', $result === false, ';END;';
''',
    'peer-checked-reversed-unset-no-init': b'''<?php
$right = true;
$calls = 0;
function comp107_noinit($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    unset($GLOBALS['right']);
    return true;
}
set_error_handler('comp107_noinit');
$a = $missing > $right;
$right = '0';
$b = $missing >= $right;
echo 'R:', $a === false, ':', $b === true, ':', !isset($right), ':', !isset($missing), ':', $calls === 2, ';END;';
''',
    'peer-checked-greaterequal-unset-supplied-throw': b'''<?php
$right = '0';
$result = 41;
$exception = new Exception('chosen107');
$calls = 0;
function comp107_throw($level, $message, $file, $line) {
    global $calls, $exception;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    unset($GLOBALS['right']);
    throw $exception;
}
set_error_handler('comp107_throw');
try {
    $result = $missing >= $right;
} catch (Exception $caught) {
    echo 'C:', $caught === $exception, ':', $result === 41, ':', !isset($right), ':', !isset($missing), ':', $calls === 1, ';';
} finally {
    echo 'F;';
}
echo 'END;';
''',
}
