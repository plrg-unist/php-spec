"""Modulo assignment preserves callback aliases when the live divisor is zero."""

CASES = {
    'modassign-float-live-zero-default': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", ($m === "Implicit conversion from float 12.5 to int loses precision"), ":", $line, ";";
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = 99;
    $GLOBALS['right'] = 0;
    return false;
}
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
    echo "C:", ($e instanceof DivisionByZeroError), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $left, ":", $alias, ":", $right, ";";
    $left = 7;
    echo "A:", $left, ":", $alias, ";";
} finally {
    echo "F;";
}
echo "END;";
''',
}
