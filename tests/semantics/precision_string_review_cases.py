"""Protected fractional text survives warning callbacks, RHS references and unset."""

CASES = {
    'precision-string-xor-complete-reference-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":";
    if ($GLOBALS['calls'] === 1) {
        echo ($m === 'Implicit conversion from float 12.5 to int loses precision'), ";";
        $GLOBALS['alias'] =& $GLOBALS['left'];
        $GLOBALS['left'] = 99;
        $GLOBALS['right'] = '-1.5';
        return true;
    }
    if ($GLOBALS['calls'] === 2) { echo ($m === 'Implicit conversion from float-string "-1.5" to int loses precision'), ";"; $GLOBALS['left'] = 88; $GLOBALS['right'] =& $GLOBALS['left']; return false; }
    echo "BAD-H;";
    return true;
}
$calls = 0;
$left = 12.5;
$right = 8.5;
$v = 100;
set_error_handler('h');

try {
    $v = ($left
        ^=
        $right);
    echo "R:", $v, ":", ($v === -13), ":", $left, ":", $alias, ":", $right, ":", $calls, ";";
    $left = 7;
    echo "A:", $left, ":", $alias, ":", $right, ";";
    $alias = 6;
    echo "B:", $left, ":", $alias, ":", $right, ";";
} catch (Throwable $e) {
    echo "BAD-C:", $e->getMessage(), ";";
} finally {
    echo "F;";
}
echo "END;";
''',
    'precision-string-shift-leading-unset-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":";
    if ($GLOBALS['calls'] === 1) { echo ($m === 'Implicit conversion from float 12.5 to int loses precision'), ";"; $GLOBALS['alias'] =& $GLOBALS['left']; $GLOBALS['left'] = 99; $GLOBALS['right'] = '-1.5tail'; return true; }
    if ($GLOBALS['calls'] === 2) {
        echo ($m === 'A non-numeric value encountered'), ";";
        $GLOBALS['left'] = 88;
        unset($GLOBALS['right']);
        return true;
    }
    if ($GLOBALS['calls'] === 3) { echo ($m === 'Implicit conversion from float-string "-1.5tail" to int loses precision'), ";"; $GLOBALS['left'] = 77; return false; }
    echo "BAD-H;";
    return true;
}
$calls = 0;
$left = 12.5;
$right = 8.5;
$v = 100;
set_error_handler('h');

try {
    $v = ($left
        >>=
        $right);
    echo "BAD-R;";
} catch (Throwable $e) {
    echo "C:", ($e instanceof ArithmeticError), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", ($left === 77), ":", ($alias === 77), ":", (!isset($right)), ":", $calls, ";";
    $left = 7;
    echo "A:", $left, ":", $alias, ":", (!isset($right)), ";";
} finally {
    echo "F;";
}
echo "END;";
''',
    'precision-string-mod-leading-zero-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":";
    if ($GLOBALS['calls'] === 1) { echo ($m === 'Implicit conversion from float 12.5 to int loses precision'), ";"; $GLOBALS['alias'] =& $GLOBALS['left']; $GLOBALS['left'] = 99; $GLOBALS['right'] = '0.5tail'; return true; }
    if ($GLOBALS['calls'] === 2) {
        echo ($m === 'A non-numeric value encountered'), ";";
        $GLOBALS['left'] = 88;
        $GLOBALS['right'] = 7;
        return false;
    }
    if ($GLOBALS['calls'] === 3) { echo ($m === 'Implicit conversion from float-string "0.5tail" to int loses precision'), ";"; $GLOBALS['left'] = 77; return false; }
    echo "BAD-H;";
    return true;
}
$calls = 0;
$left = 12.5;
$right = 8.5;
$v = 100;
set_error_handler('h');

try {
    $v = ($left
        %=
        $right);
    echo "BAD-R;";
} catch (Throwable $e) {
    echo "C:", ($e instanceof DivisionByZeroError), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", ($left === 77), ":", ($alias === 77), ":", ($right === 7), ":", $calls, ";";
    $left = 7;
    echo "A:", $left, ":", $alias, ":", $right, ";";
} finally {
    echo "F;";
}
echo "END;";
''',
}
