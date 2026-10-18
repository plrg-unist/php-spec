"""Independent mixed CV/reference pointers, historical holders and live labels."""

CASES = {
    'mixed-arithmetic-selected-right-float-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $ok = $GLOBALS['calls'] === 1 ? ($GLOBALS['left'] === '12.5tail' && $GLOBALS['right'] === 'bad' && $GLOBALS['rightAlias'] === 'bad') : ($GLOBALS['left'] === 99 && $GLOBALS['right'] === '2tail' && $GLOBALS['rightAlias'] === '5.5tail');
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ':', $ok, ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered') { echo 'BAD-H;'; return true; }
    if ($GLOBALS['calls'] === 1) {
        $GLOBALS['left'] = 99; $GLOBALS['rightAlias'] = '5.5tail';
        $GLOBALS['right'] =& $GLOBALS['replacement']; return true;
    }
    $GLOBALS['left'] = false; $GLOBALS['rightAlias'] = 'bad'; return false;
}
set_error_handler('h'); $calls = 0;
$left = '12.5tail'; $right = 'bad'; $rightAlias =& $right; $replacement = '2tail'; $v = 100;






try {
    $v =
        $left
        *
        $right;
    echo 'R:', $v, ':', $v === 68.75, ':', $left === false, ':', $right === '2tail', ':', $rightAlias === 'bad', ':', $replacement === '2tail', ':', $calls === 2, ';';
} catch (Throwable $e) { echo 'BAD-E:', $e->getMessage(), ';'; }
finally { echo 'F;'; }
$left = 7; $right = 8; $rightAlias = 6;
echo 'A:', $left === 7, ':', $right === 8, ':', $replacement === 8, ':', $rightAlias === 6, ';END;';
''',
    'mixed-arithmetic-selected-left-types-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ':', $GLOBALS['leftAlias'] === '2tail' && $GLOBALS['left'] === '2tail' && $GLOBALS['right'] === 'bad', ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered') { echo 'BAD-H;'; return true; }
    $GLOBALS['leftAlias'] = false; $GLOBALS['left'] =& $GLOBALS['replacement'];
    return false;
}
set_error_handler('h'); $calls = 0;
$left = '2tail'; $leftAlias =& $left; $right = 'bad'; $replacement = 99; $v = 100;










try {
    $v =
        $left
        -
        $right;
    echo 'BAD-R;';
} catch (Throwable $e) {
    echo 'E:', $e instanceof TypeError, ':', $e->getMessage() === 'Unsupported operand types: bool - string', ':', $e->getLine(), ':', $e->getPrevious() === null, ':', $v === 100, ':', $left === 99, ':', $leftAlias === false, ':', $right === 'bad', ':', $replacement === 99, ':', $calls === 1, ';';
} finally { echo 'F;'; }
$left = 7; $leftAlias = 6; $right = 8;
echo 'A:', $left === 7, ':', $replacement === 7, ':', $leftAlias === 6, ':', $right === 8, ';END;';
''',
    'mixed-arithmetic-selected-zero-unset-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ':', $GLOBALS['left'] === 12 && $GLOBALS['right'] === '0tail' && $GLOBALS['rightAlias'] === '0tail', ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered') { echo 'BAD-H;'; return true; }
    $GLOBALS['left'] = false; $GLOBALS['rightAlias'] = 7; unset($GLOBALS['right']);
    return false;
}
set_error_handler('h'); $calls = 0;
$left = 12; $right = '0tail'; $rightAlias =& $right; $v = 100;










try {
    $v =
        $left
        /
        $right;
    echo 'BAD-R;';
} catch (Throwable $e) {
    echo 'E:', $e instanceof DivisionByZeroError, ':', $e->getMessage() === 'Division by zero', ':', $e->getLine(), ':', $e->getPrevious() === null, ':', $v === 100, ':', $left === false, ':', $rightAlias === 7, ':', !isset($right), ':', $calls === 1, ';';
} finally { echo 'F;'; }
$left = 7; $right = 8; $rightAlias = 6;
echo 'A:', $left === 7, ':', $right === 8, ':', $rightAlias === 6, ';END;';
''',
}
