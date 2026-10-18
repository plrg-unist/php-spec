"""Independent plain-slot holders, late references, live errors and unsetting."""

CASES = {
    'plain-arithmetic-mul-late-reference-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered') { echo 'BAD-H;'; return true; }
    if ($GLOBALS['calls'] === 1) {
        $GLOBALS['left'] = 99; $GLOBALS['right'] = '5.5tail';
        return true;
    }
    $GLOBALS['left'] = false;
    $GLOBALS['rightAlias'] =& $GLOBALS['right'];
    $GLOBALS['rightAlias'] = 'bad';
    return false;
}
set_error_handler('h'); $calls = 0;
$left = '12.5tail'; $right = 'bad'; $v = 100;




try {
    $v =
        $left
        *
        $right;
    echo 'R:', $v, ':', $v === 68.75, ':', $left === false, ':', $right === 'bad', ':', $rightAlias === 'bad', ':', $calls === 2, ';';
} catch (Throwable $e) { echo 'BAD-E:', $e->getMessage(), ';'; }
finally { echo 'F;'; }
$left = 7; $right = 8;
echo 'A:', $rightAlias === 8, ':', $left === 7, ';END;';
''',
    'plain-arithmetic-live-types-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered') { echo 'BAD-H;'; return true; }
    $GLOBALS['left'] = false;
    return false;
}
set_error_handler('h'); $calls = 0;
$left = '2tail'; $right = 'bad'; $v = 100;










try {
    $v =
        $left
        -
        $right;
    echo 'BAD-R;';
} catch (Throwable $e) {
    echo 'E:', $e instanceof TypeError, ':', $e->getMessage() === 'Unsupported operand types: bool - string', ':', $e->getLine(), ':', $e->getPrevious() === null, ':', $v === 100, ':', $left === false, ':', $right === 'bad', ':', $calls === 1, ';';
} finally { echo 'F;'; }
$left = 7; $right = 8;
echo 'A:', $left === 7, ':', $right === 8, ';END;';
''',
    'plain-arithmetic-div-unset-after-capture': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered') { echo 'BAD-H;'; return true; }
    $GLOBALS['left'] = 99;
    unset($GLOBALS['right']);
    return false;
}
set_error_handler('h'); $calls = 0;
$left = 12; $right = '2tail'; $v = 100;









try {
    $v =
        $left
        /
        $right;
    echo 'R:', $v, ':', $v === 6, ':', $left === 99, ':', !isset($right), ':', $calls === 1, ';';
} catch (Throwable $e) { echo 'BAD-E:', $e->getMessage(), ';'; }
finally { echo 'F;'; }
$left = 7; $right = 8;
echo 'A:', $left === 7, ':', $right === 8, ';END;';
''',
}
