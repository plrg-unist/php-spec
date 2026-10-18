"""Independent power holders, live failures, and signed-zero diagnostic order."""

CASES = {
    'power-conversion-fractional-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered') { echo 'BAD-H;'; return true; }
    if ($GLOBALS['calls'] === 1) {
        $GLOBALS['left'] = 99;
        $GLOBALS['right'] = '0.5tail';
        return true;
    }
    $GLOBALS['left'] = false;
    $GLOBALS['right'] = 'bad';
    return false;
}
set_error_handler('h');
$calls = 0;
$left = '4.0tail'; $leftAlias =& $left;
$right = 'bad'; $rightAlias =& $right;
$v = 100;

try {
    $v =
        $left
        **
        $right;
    echo 'R:', $v, ':', $v === 2.0, ':', $left === false, ':', $leftAlias === false, ':', $right === 'bad', ':', $rightAlias === 'bad', ':', $calls === 2, ';';
} catch (Throwable $e) { echo 'BAD-E:', $e->getMessage(), ';'; }
finally { echo 'F;'; }
$left = 7; $right = 8;
echo 'A:', $leftAlias === 7, ':', $rightAlias === 8, ';END;';
''',
    'power-conversion-live-types-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered') { echo 'BAD-H;'; return true; }
    $GLOBALS['left'] = false;
    return false;
}
set_error_handler('h');
$calls = 0;
$left = '2tail'; $leftAlias =& $left;
$right = 'bad'; $rightAlias =& $right;
$v = 100;







try {
    $v =
        $left
        **
        $right;
    echo 'BAD-R;';
} catch (Throwable $e) {
    echo 'E:', $e instanceof TypeError, ':', $e->getMessage() === 'Unsupported operand types: bool ** string', ':', $e->getLine(), ':', $e->getPrevious() === null, ':', $v === 100, ':', $left === false, ':', $leftAlias === false, ':', $right === 'bad', ':', $rightAlias === 'bad', ':', $calls === 1, ';';
} finally { echo 'F;'; }
$left = 7; $right = 8;
echo 'A:', $leftAlias === 7, ':', $rightAlias === 8, ';END;';
''',
    'power-conversion-negative-zero-old-right-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $expected = $GLOBALS['calls'] < 3 ? 'A non-numeric value encountered' : 'Power of base 0 and negative exponent is deprecated';
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === $expected, ';';
    if ($line !== 25 || $m !== $expected || ($GLOBALS['calls'] < 3 ? $n !== 2 : $n !== 8192)) { echo 'BAD-H;'; return true; }
    if ($GLOBALS['calls'] === 1) {
        $GLOBALS['left'] = 99; $GLOBALS['right'] = '-3tail';
        $GLOBALS['right'] =& $GLOBALS['replacement'];
        return true;
    }
    if ($GLOBALS['calls'] === 2) {
        $GLOBALS['left'] = 88; $GLOBALS['rightAlias'] = 7;
        return true;
    }
    $GLOBALS['left'] = 4; $GLOBALS['rightAlias'] = 9; return false;
}
set_error_handler('h'); $calls = 0;
$left = '-0.0tail'; $leftAlias =& $left; $right = 'bad'; $rightAlias =& $right; $replacement = '2tail';
$v = 100;
try {
    $v =
        $left
        **
        $right;
    echo 'R:', $v, ':', $v === -1e999, ':', $left === 4, ':', $leftAlias === 4, ':', $right === '2tail', ':', $replacement === '2tail', ':', $rightAlias === 9, ':', $calls === 3, ';';
} catch (Throwable $e) { echo 'BAD-E:', $e->getMessage(), ';'; }
finally { echo 'F;'; }
$rightAlias = 6; $left = 7;
echo 'A:', $leftAlias === 7, ':', $rightAlias === 6, ':', $right === '2tail', ':', $replacement === '2tail', ';';
$right = 8;
echo 'B:', $replacement === 8, ':', $rightAlias === 6, ';END;';
''',
}
