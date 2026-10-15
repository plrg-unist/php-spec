"""Compound shifts retain both longs before a fractional-count diagnostic."""

LEFT_WRITE = b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", ($m === "Implicit conversion from float 2.5 to int loses precision"), ":", $line, ";";
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = 99;
    $GLOBALS['right'] = 1;
    return true;
}
$left = -12; $right = 2.5; $v = 100;
set_error_handler("h");
try {
    $v = ($left <<=
        $right);
    echo "R:", $v, ":", ($v === -48), ":", $left, ":", $alias, ":", $right, ";";
    $left = 7;
    echo "A:", $left, ":", $alias, ";";
} catch (Throwable $e) { echo "BAD-C;"; }
finally { echo "F;"; }
echo "END;";
'''

CASES = {
    'shiftassign-right-left-handler-write': LEFT_WRITE,
    'shiftassign-right-right-handler-write': LEFT_WRITE.replace(b'<<=', b'>>=').replace(b'=== -48', b'=== -3'),
    'shiftassign-right-left-handler-throw': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", ($m === "Implicit conversion from float 2.5 to int loses precision"), ":", $line, ";";
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = 99;
    $GLOBALS['right'] = 1;
    throw $GLOBALS['second'];
}
$left = -12; $right = 2.5; $v = 100;
$second = new Exception("second");
set_error_handler("h");
try {
    $v = ($left <<=
        $right);
    echo "BODY;";
} catch (Throwable $e) {
    echo "C:", ($e === $second), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $left, ":", $alias, ":", $right, ";";
    $left = 7;
    echo "A:", $left, ":", $alias, ";";
} finally { echo "F;"; }
echo "END;";
''',
}
