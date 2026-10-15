"""A cached negative RIGHT remains a signed XOR mask after live rewrites."""

CASES = {
    'bitassign-right-xor-negative-default': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", ($m === "Implicit conversion from float -1.5 to int loses precision"), ":", $line, ";";
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = 99;
    $GLOBALS['right'] = 10;
    return false;
}
$left = 12;
$right = -1.5;
$v = 100;
set_error_handler('h');
try {
    $v = ($left
        ^=
        $right);
    echo "R:", $v, ":", ($v === -13), ":", $left, ":", $alias, ":", $right, ";";
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
