"""Compound bitwise assignments cache both longs before a fractional-RHS warning."""

AND_WRITE = b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", ($m === "Implicit conversion from float 5.5 to int loses precision"), ":", $line, ";";
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = 99;
    $GLOBALS['right'] = 10;
    return true;
}
$left = 12; $right = 5.5; $v = 100;
set_error_handler("h");
try {
    $v = ($left &=
        $right);
    echo "R:", $v, ":", ($v === 4), ":", $left, ":", $alias, ":", $right, ";";
    $left = 7;
    echo "A:", $left, ":", $alias, ";";
} catch (Throwable $e) { echo "BAD-C;"; }
finally { echo "F;"; }
echo "END;";
'''

CASES = {
    'bitassign-right-and-handler-write': AND_WRITE,
    'bitassign-right-or-handler-write': AND_WRITE.replace(b'&=', b'|=').replace(b'=== 4', b'=== 13'),
    'bitassign-right-xor-handler-write': AND_WRITE.replace(b'&=', b'^=').replace(b'=== 4', b'=== 9'),
    'bitassign-right-and-handler-throw': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", ($m === "Implicit conversion from float 5.5 to int loses precision"), ":", $line, ";";
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = 99;
    $GLOBALS['right'] = 10;
    throw $GLOBALS['second'];
}
$left = 12; $right = 5.5; $v = 100;
$second = new Exception("second");
set_error_handler("h");
try {
    $v = ($left &=
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
