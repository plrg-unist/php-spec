"""Integral float counts convert quietly after the first shift deprecation."""

LEFT = b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":";
    if ($GLOBALS['calls'] === 1) {
        echo ($m === "Implicit conversion from float -12.5 to int loses precision"), ";";
        $GLOBALS['alias'] =& $GLOBALS['left'];
        $GLOBALS['left'] = 99;
        $GLOBALS['right'] = 2.0;
        if ($GLOBALS['throw_at'] === 1) { throw $GLOBALS['second']; }
        return true;
    }
    echo ($m === "Implicit conversion from float 2.5 to int loses precision"), ";";
    $GLOBALS['left'] = 88;
    $GLOBALS['right'] = 1;
    if ($GLOBALS['throw_at'] === 2) { throw $GLOBALS['second']; }
    return true;
}
$calls = 0; $throw_at = 0;
$left = -12.5; $right = 8.5; $v = 100;
$second = new Exception("second");
set_error_handler("h");
try {
    $v = ($left <<=
        $right);
    echo "R:", $v, ":", ($v === -48), ":", $left, ":", $alias, ":", $right, ":", ($right === 2.0), ":", $calls, ";";
} catch (Throwable $e) {
    echo "C:", ($e === $second), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $left, ":", $alias, ":", $right, ":", ($right === 2.0), ":", $calls, ";";
} finally { echo "F;"; }
$left = 7;
echo "A:", $left, ":", $alias, ";END;";
'''

RIGHT = LEFT.replace(b'$left <<=', b'$left >>=').replace(b'$v === -48', b'$v === -3')

CASES = {
    'shiftassign-quiet-float-left-handler-write': LEFT,
    'shiftassign-quiet-float-right-handler-write': RIGHT,
    'shiftassign-quiet-float-left-handler-throw': LEFT.replace(b'$throw_at = 0;', b'$throw_at = 1;'),
}
