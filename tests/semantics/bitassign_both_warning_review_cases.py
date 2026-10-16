"""A second fractional RHS keeps its negative mask after a positive rewrite."""

CASES = {
    'bitassign-both-cached-negative-default': b'''<?php
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
    $GLOBALS['right'] = 10;
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
    echo "A:", $left, ":", $alias, ";";
} catch (Throwable $e) {
    echo "BAD-C:", $e->getMessage(), ";";
} finally {
    echo "F;";
}
echo "END;";
''',
}
