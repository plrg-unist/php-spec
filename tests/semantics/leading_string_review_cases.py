"""Second-warning callbacks may rebind or unset an already converted RHS."""

CASES = {
    'leading-string-xor-reference-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":";
    if ($GLOBALS['calls'] === 1) {
        echo ($m === "Implicit conversion from float 12.5 to int loses precision"), ";";
        $GLOBALS['alias'] =& $GLOBALS['left'];
        $GLOBALS['left'] = 99;
        $GLOBALS['right'] = '-1tail';
        return true;
    }
    echo ($m === "A non-numeric value encountered"), ";";
    $GLOBALS['left'] = 88;
    $GLOBALS['right'] =& $GLOBALS['left'];
    return false;
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
    'leading-string-shift-unset-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":";
    if ($GLOBALS['calls'] === 1) {
        echo ($m === "Implicit conversion from float 12.5 to int loses precision"), ";";
        $GLOBALS['alias'] =& $GLOBALS['left'];
        $GLOBALS['left'] = 99;
        $GLOBALS['right'] = '-1tail';
        return true;
    }
    echo ($m === "A non-numeric value encountered"), ";";
    $GLOBALS['left'] = 88;
    unset($GLOBALS['right']);
    return false;
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
    echo "C:", ($e instanceof ArithmeticError), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $left, ":", $alias, ":", (!isset($right)), ":", $calls, ";";
    $left = 7;
    echo "A:", $left, ":", $alias, ";";
} finally {
    echo "F;";
}
echo "END;";
''',
    'leading-string-mod-zero-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":";
    if ($GLOBALS['calls'] === 1) {
        echo ($m === "Implicit conversion from float 12.5 to int loses precision"), ";";
        $GLOBALS['alias'] =& $GLOBALS['left'];
        $GLOBALS['left'] = 99;
        $GLOBALS['right'] = '0tail';
        return true;
    }
    echo ($m === "A non-numeric value encountered"), ";";
    $GLOBALS['left'] = 88;
    $GLOBALS['right'] = 7;
    return false;
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
    echo "C:", ($e instanceof DivisionByZeroError), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $left, ":", $alias, ":", $right, ":", $calls, ";";
    $left = 7;
    echo "A:", $left, ":", $alias, ";";
} finally {
    echo "F;";
}
echo "END;";
''',
}
