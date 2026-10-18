"""Quiet-LEFT right-only Warning caches, zero error and final power history."""

CASES = {
    'right-warning-mul-fractional-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered') { echo 'BAD-H;'; return true; }
    $GLOBALS['left'] = false;
    $GLOBALS['right'] = 'bad';
    return false;
}
set_error_handler('h'); $calls = 0;
$left = '12.5'; $leftAlias =& $left;
$right = '5.5tail'; $rightAlias =& $right;
$v = 100;







try {
    $v =
        $left
        *
        $right;
    echo 'R:', $v, ':', $v === 68.75, ':', $left === false, ':', $leftAlias === false, ':', $right === 'bad', ':', $rightAlias === 'bad', ':', $calls === 1, ';';
} catch (Throwable $e) { echo 'BAD-E:', $e->getMessage(), ';'; }
finally { echo 'F;'; }
$left = 7; $right = 8;
echo 'A:', $leftAlias === 7, ':', $rightAlias === 8, ';END;';
''',
    'right-warning-div-zero-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered') { echo 'BAD-H;'; return true; }
    $GLOBALS['left'] = false;
    $GLOBALS['right'] = 7;
    return false;
}
set_error_handler('h'); $calls = 0;
$left = 12; $leftAlias =& $left;
$right = '0tail'; $rightAlias =& $right;
$v = 100;







try {
    $v =
        $left
        /
        $right;
    echo 'BAD-R;';
} catch (Throwable $e) {
    echo 'E:', $e instanceof DivisionByZeroError, ':', $e->getMessage() === 'Division by zero', ':', $e->getLine(), ':', $e->getPrevious() === null, ':', $v === 100, ':', $left === false, ':', $leftAlias === false, ':', $right === 7, ':', $rightAlias === 7, ':', $calls === 1, ';';
} finally { echo 'F;'; }
$left = 7; $right = 8;
echo 'A:', $leftAlias === 7, ':', $rightAlias === 8, ';END;';
''',
    'right-warning-power-negative-zero-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $expected = $GLOBALS['calls'] === 1 ? 'A non-numeric value encountered' : 'Power of base 0 and negative exponent is deprecated';
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === $expected, ';';
    if ($line !== 25 || $m !== $expected || ($GLOBALS['calls'] === 1 ? $n !== 2 : $n !== 8192)) { echo 'BAD-H;'; return true; }
    if ($GLOBALS['calls'] === 1) {
        $GLOBALS['left'] = 99; $GLOBALS['right'] = 7;
        $GLOBALS['right'] =& $GLOBALS['replacement'];
        return true;
    }
    $GLOBALS['left'] = 4; $GLOBALS['rightAlias'] = 9; return false;
}
set_error_handler('h'); $calls = 0;
$left = -0.0; $leftAlias =& $left; $right = '-3tail'; $rightAlias =& $right; $replacement = '2tail';
$v = 100;




try {
    $v =
        $left
        **
        $right;
    echo 'R:', $v, ':', $v === -1e999, ':', $left === 4, ':', $leftAlias === 4, ':', $right === '2tail', ':', $replacement === '2tail', ':', $rightAlias === 9, ':', $calls === 2, ';';
} catch (Throwable $e) { echo 'BAD-E:', $e->getMessage(), ';'; }
finally { echo 'F;'; }
$rightAlias = 6; $left = 7;
echo 'A:', $leftAlias === 7, ':', $rightAlias === 6, ':', $right === '2tail', ':', $replacement === '2tail', ';';
$right = 8;
echo 'B:', $replacement === 8, ':', $rightAlias === 6, ';END;';
''',
}
