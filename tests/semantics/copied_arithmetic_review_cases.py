"""Independent copied arithmetic inputs, raw types and surviving holders."""

CASES = {
    'copied-arithmetic-right-bad-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ':', $GLOBALS['left'] === '12tail' && $GLOBALS['leftAlias'] === '12tail' && $GLOBALS['right'] === 'bad', ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered') { echo 'BAD-H;'; return true; }
    $GLOBALS['leftAlias'] = false; $GLOBALS['right'] = '5tail'; return false;
}
set_error_handler('h'); $calls = 0;
$left = '12tail'; $leftAlias =& $left; $right = 'bad'; $v = 100;











try {
    $v =
        $left
        -
        (true ? $right : 0);
echo 'BAD-R;';
} catch (Throwable $e) {
    echo 'E:', $e instanceof TypeError, ':', $e->getMessage() === 'Unsupported operand types: bool - string', ':', $e->getLine(), ':', $e->getPrevious() === null, ':', $v === 100, ':', $left === false, ':', $leftAlias === false, ':', $right === '5tail', ':', $calls === 1, ';';
} finally { echo 'F;'; }
$left = 7; $leftAlias = 6; $right = 8;
echo 'A:', $left === 6, ':', $leftAlias === 6, ':', $right === 8, ';END;';
''',
    'copied-arithmetic-left-types-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ':', $GLOBALS['left'] === '12tail' && $GLOBALS['right'] === 'bad', ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered') { echo 'BAD-H;'; return true; }
    $GLOBALS['left'] = false; $GLOBALS['right'] = 'bad'; return false;
}
set_error_handler('h'); $calls = 0;
$left = '12tail'; $right = 'bad'; $v = 100;











try {
    $v =
        (true ? $left : 0)
        +
        $right;
echo 'BAD-R;';
} catch (Throwable $e) {
    echo 'E:', $e instanceof TypeError, ':', $e->getMessage() === 'Unsupported operand types: string + string', ':', $e->getLine(), ':', $e->getPrevious() === null, ':', $v === 100, ':', $left === false, ':', $right === 'bad', ':', $calls === 1, ';';
} finally { echo 'F;'; }
$left = 7; $right = 8;
echo 'A:', $left === 7, ':', $right === 8, ';END;';
''',
    'copied-arithmetic-both-float-unset-default': b'''<?php
function lhs() { return $GLOBALS['left']; }
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ':', $GLOBALS['left'] === '12.5' && $GLOBALS['right'] === '5.5tail', ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered') { echo 'BAD-H;'; return true; }
    unset($GLOBALS['left'], $GLOBALS['right']); return false;
}
set_error_handler('h'); $calls = 0;
$left = '12.5'; $right = '5.5tail'; $v = 100;










try {
    $v =
        lhs()
        *
        (true ? $right : 0);
echo 'R:', $v, ':', $v === 68.75, ':', !isset($left), ':', !isset($right), ':', $calls === 1, ';';
} catch (Throwable $e) { echo 'BAD-E:', $e->getMessage(), ';'; }
finally { echo 'F;'; }
$left = 7; $right = 8;
echo 'A:', $left === 7, ':', $right === 8, ';END;';
''',
}
