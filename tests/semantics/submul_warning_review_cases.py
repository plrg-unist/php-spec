"""Independent numeric holders, live failure types, and selected-referent originals."""

CASES = {
    'submul-mul-fractional-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered') { echo 'BAD-H;'; return true; }
    if ($GLOBALS['calls'] === 1) {
        $GLOBALS['left'] = 99;
        $GLOBALS['right'] = '5.5tail';
        return true;
    }
    $GLOBALS['left'] = false;
    $GLOBALS['right'] = 'bad';
    return false;
}
set_error_handler('h');
$calls = 0;
$left = '12.5tail'; $leftAlias =& $left;
$right = 'bad'; $rightAlias =& $right;
$v = 100;

try {
    $v =
        $left
        *
        $right;
    echo 'R:', $v, ':', $v === 68.75, ':', $left === false, ':', $leftAlias === false, ':', $right === 'bad', ':', $rightAlias === 'bad', ':', $calls === 2, ';';
} catch (Throwable $e) { echo 'BAD-E:', $e->getMessage(), ';'; }
finally { echo 'F;'; }
$left = 7; $right = 8;
echo 'A:', $leftAlias === 7, ':', $rightAlias === 8, ';END;';
''',
    'submul-sub-live-types-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered') { echo 'BAD-H;'; return true; }
    $GLOBALS['left'] = false;
    return false;
}
set_error_handler('h');
$calls = 0;
$left = '12tail'; $leftAlias =& $left;
$right = 'bad'; $rightAlias =& $right;
$v = 100;







try {
    $v =
        $left
        -
        $right;
    echo 'BAD-R;';
} catch (Throwable $e) {
    echo 'E:', $e instanceof TypeError, ':', $e->getMessage() === 'Unsupported operand types: bool - string', ':', $e->getLine(), ':', $e->getPrevious() === null, ':', $v === 100, ':', $left === false, ':', $leftAlias === false, ':', $right === 'bad', ':', $rightAlias === 'bad', ':', $calls === 1, ';';
} finally { echo 'F;'; }
$left = 7; $right = 8;
echo 'A:', $leftAlias === 7, ':', $rightAlias === 8, ';END;';
''',
    'submul-sub-selected-old-right-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered') { echo 'BAD-H;'; return true; }
    if ($GLOBALS['calls'] === 1) {
        $GLOBALS['left'] = 99;
        $GLOBALS['right'] = '5tail';
        $GLOBALS['right'] =& $GLOBALS['replacement'];
        return true;
    }
    $GLOBALS['left'] = 88;
    $GLOBALS['rightAlias'] = 7;
    return false;
}
set_error_handler('h');
$calls = 0;
$left = '12tail'; $leftAlias =& $left;
$right = 'bad'; $rightAlias =& $right; $replacement = '100tail';
$v = 100;
try {
    $v =
        $left
        -
        $right;
    echo 'R:', $v, ':', $v === 7, ':', $left === 88, ':', $leftAlias === 88, ':', $right === '100tail', ':', $replacement === '100tail', ':', $rightAlias === 7, ':', $calls === 2, ';';
} catch (Throwable $e) { echo 'BAD-E:', $e->getMessage(), ';'; }
finally { echo 'F;'; }
$rightAlias = 6; $left = 7;
echo 'A:', $leftAlias === 7, ':', $rightAlias === 6, ':', $right === '100tail', ':', $replacement === '100tail', ';';
$right = 8;
echo 'B:', $replacement === 8, ':', $rightAlias === 6, ';END;';
''',
}
