"""A saved negative LEFT and live RHS determine signed XOR assignment."""

CASES = {
    'bitassign-xor-negative-default': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", ($m === "Implicit conversion from float -12.5 to int loses precision"), ":", $line, ";";
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = 99;
    $GLOBALS['right'] = 5;
    return false;
}
$left = -12.5;
$right = 3;
$v = 100;
set_error_handler('h');
try {
    $v = ($left
        ^=
        $right);
    echo "R:", $v, ":", ($v === -15), ":", $left, ":", $alias, ":", $right, ";";
    $left = 7;
    echo "A:", $left, ":", $alias, ";";
} catch (Throwable $e) {
    echo "BAD-C:", $e->getMessage(), ";";
} finally {
    echo "F;";
}
echo "END;";
''',
}
