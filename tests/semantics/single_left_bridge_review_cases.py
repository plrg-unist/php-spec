"""An initially quiet RHS changes to null, a negative float or an array."""

CASES = {
    'single-left-bridge-mod-null-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:",
        $GLOBALS['calls'], ":", $n, ":",
        $line, ":";
    if ($GLOBALS['calls'] === 1) {
        echo ($m === "Implicit conversion from float 12.5 to int loses precision"), ";";
        $GLOBALS['alias'] =& $GLOBALS['left'];
        $GLOBALS['left'] = 99;
        $GLOBALS['right'] = null;
        return false;
    }
    echo "BAD-H;";
    return true;
}
$calls = 0;
$left = 12.5;
$right = 3;
$v = 100;
set_error_handler('h');
try {
    $v = ($left
        %=
        $right);
    echo "BAD-R;";
} catch (Throwable $e) {
    echo "C:", ($e instanceof DivisionByZeroError), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $left, ":", $alias, ":", ($right === null), ":", $calls, ";";
    $left = 7;
    echo "A:", $left, ":", $alias, ";";
} finally {
    echo "F;";
}
echo "END;";
''',
    'single-left-bridge-xor-negative-reference-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":";
    if ($GLOBALS['calls'] === 1) {
        echo ($m === "Implicit conversion from float 12.5 to int loses precision"), ";";
        $GLOBALS['alias'] =& $GLOBALS['left'];
        $GLOBALS['left'] = 99;
        $GLOBALS['right'] = -1.5;
        return true;
    }
    echo ($m === "Implicit conversion from float -1.5 to int loses precision"), ";";
    $GLOBALS['left'] = 88;
    $GLOBALS['right'] =& $GLOBALS['left'];
    return false;
}
$calls = 0;
$left = 12.5;
$right = 3;
$v = 100;
set_error_handler('h');
try {
    $v = ($left
        ^=
        $right);
    echo "R:", $v, ":", ($v === -13), ":", $left, ":", $alias, ":", $right, ":", $calls, ";";
    $left = 7;
    $alias = 6;
    echo "A:", $left, ":", $alias, ":", $right, ";";
} catch (Throwable $e) {
    echo "BAD-C:", $e->getMessage(), ";";
} finally {
    echo "F;";
}
echo "END;";
''',
    'single-left-bridge-shift-array-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":",
        $n, ":", $line, ":";
    echo ($m ===
        "Implicit conversion from float 12.5 to int loses precision"), ";";
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = false;
    $GLOBALS['right'] = [3];
    return false;
}

$calls = 0;
$left = 12.5;
$right = 3;
$v = 100;
set_error_handler(
    'h'
);

try {
    $v = ($left
        >>=
        $right);
    echo "BAD-R;";
} catch (Throwable $e) {
    echo "C:", ($e instanceof TypeError), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", ($left === false), ":", ($alias === false), ":", ($right[0] === 3), ":", $calls, ";";
    $left = 7;
    echo "A:", $left, ":", $alias, ":", ($right[0] === 3), ";";
} finally {
    echo "F;";
}
echo "END;";
''',
}
