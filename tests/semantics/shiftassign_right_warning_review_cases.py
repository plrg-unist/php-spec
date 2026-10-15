"""RHS shift conversion keeps a negative count and a wide count's signed result."""

CASES = {
    'shiftassign-right-cached-negative-default': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", ($m === "Implicit conversion from float -1.5 to int loses precision"), ":", $line, ";";
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = 99;
    $GLOBALS['right'] = 2;
    return false;
}
$left = 12;
$right = -1.5;
$v = 100;
set_error_handler('h');
try {
    $v = ($left
        >>=
        $right);
    echo "BAD-R;";
} catch (Throwable $e) {
    echo "C:", ($e instanceof ArithmeticError), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $left, ":", $alias, ":", $right, ";";
    $left = 7;
    echo "A:", $left, ":", $alias, ";";
} finally {
    echo "F;";
}
echo "END;";
''',
    'shiftassign-right-cached-wide-default': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", ($m === "Implicit conversion from float 64.5 to int loses precision"), ":", $line, ";";
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = 99;
    $GLOBALS['right'] = 2;
    return false;
}
$left = -12;
$right = 64.5;
$v = 100;
set_error_handler('h');
try {
    $v = ($left
        >>=
        $right);
    echo "R:", $v, ":", ($v === -1), ":", $left, ":", $alias, ":", $right, ";";
    $left = 7;
    echo "A:", $left, ":", $alias, ";";
} catch (Throwable $e) {
    echo "BAD-C;";
} finally {
    echo "F;";
}
echo "END;";
''',
}
