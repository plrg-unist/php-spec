"""Independent owned arithmetic references, alias multiplicity and retirement."""

CASES = {
    'owned-arithmetic-same-cell-default': b'''<?php
function &lhs() { $GLOBALS['sourceCalls'] = $GLOBALS['sourceCalls'] + 1; return $GLOBALS['shared']; }
function &rhs() { $GLOBALS['sourceCalls'] = $GLOBALS['sourceCalls'] + 1; return $GLOBALS['shared']; }
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $ok = $GLOBALS['calls'] === 1 ? ($GLOBALS['shared'] === '12tail' && $GLOBALS['sourceCalls'] === 2) : (!isset($GLOBALS['shared']) && $GLOBALS['sourceCalls'] === 2);
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ':', $ok, ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered') { echo 'BAD-H;'; return true; }
    if ($GLOBALS['calls'] === 1) { $GLOBALS['shared'] = '5tail'; unset($GLOBALS['shared']); return true; }
    $GLOBALS['shared'] = 88; return false;
}
set_error_handler('h'); $calls = 0; $sourceCalls = 0;
$shared = '12tail'; $v = 100;







try {
    $v =
        lhs()
        +
        rhs();
echo 'R:', $v, ':', $v === 17, ':', $shared === 88, ':', $calls === 2, ':', $sourceCalls === 2, ';';
} catch (Throwable $e) { echo 'BAD-E:', $e->getMessage(), ';'; }
finally { echo 'F;'; }
$shared = 7;
echo 'A:', $shared === 7, ';END;';
''',
    'owned-arithmetic-left-types-default': b'''<?php
function &lhs() { $GLOBALS['sourceCalls'] = $GLOBALS['sourceCalls'] + 1; return $GLOBALS['left']; }
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ':', $GLOBALS['left'] === '12tail' && $GLOBALS['right'] === 'bad' && $GLOBALS['sourceCalls'] === 1, ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered') { echo 'BAD-H;'; return true; }
    $GLOBALS['left'] = false; $GLOBALS['right'] = '5tail'; unset($GLOBALS['left']); return false;
}
set_error_handler('h'); $calls = 0; $sourceCalls = 0;
$left = '12tail'; $right = 'bad'; $v = 100;










try {
    $v =
        lhs()
        -
        (true ? $right : 0);
echo 'BAD-R;';
} catch (Throwable $e) {
    echo 'E:', $e instanceof TypeError, ':', $e->getMessage() === 'Unsupported operand types: bool - string', ':', $e->getLine(), ':', $e->getPrevious() === null, ':', $v === 100, ':', !isset($left), ':', $right === '5tail', ':', $calls === 1, ':', $sourceCalls === 1, ';';
} finally { echo 'F;'; }
$left = 7; $right = 8;
echo 'A:', $left === 7, ':', $right === 8, ';END;';
''',
    'owned-arithmetic-zero-unset-default': b'''<?php
function &rhs() { $GLOBALS['sourceCalls'] = $GLOBALS['sourceCalls'] + 1; return $GLOBALS['right']; }
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ':', $GLOBALS['left'] === 12 && $GLOBALS['right'] === '0tail' && $GLOBALS['sourceCalls'] === 1, ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered') { echo 'BAD-H;'; return true; }
    $GLOBALS['left'] = false; $GLOBALS['right'] = 7; unset($GLOBALS['right']); return false;
}
set_error_handler('h'); $calls = 0; $sourceCalls = 0;
$left = 12; $right = '0tail'; $v = 100;










try {
    $v =
        (+$left)
        /
        rhs();
echo 'BAD-R;';
} catch (Throwable $e) {
    echo 'E:', $e instanceof DivisionByZeroError, ':', $e->getMessage() === 'Division by zero', ':', $e->getLine(), ':', $e->getPrevious() === null, ':', $v === 100, ':', $left === false, ':', !isset($right), ':', $calls === 1, ':', $sourceCalls === 1, ';';
} finally { echo 'F;'; }
$left = 7; $right = 8;
echo 'A:', $left === 7, ':', $right === 8, ';END;';
''',
}
