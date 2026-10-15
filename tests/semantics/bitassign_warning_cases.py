"""Compound bitwise assignments retain the first long and read the live RHS."""

AND_WRITE = b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", ($m === "Implicit conversion from float 12.5 to int loses precision"), ":", $line, ";";
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = 99;
    $GLOBALS['right'] = 5;
    return true;
}
$left = 12.5; $right = 3; $v = 100;
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
    'bitassign-and-handler-write': AND_WRITE,
    'bitassign-or-handler-write': AND_WRITE.replace(b'&=', b'|=').replace(b'=== 4', b'=== 13'),
    'bitassign-xor-handler-write': AND_WRITE.replace(b'&=', b'^=').replace(b'=== 4', b'=== 9'),
    'bitassign-and-handler-throw': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", ($m === "Implicit conversion from float 12.5 to int loses precision"), ":", $line, ";";
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = 99;
    $GLOBALS['right'] = 5;
    throw $GLOBALS['second'];
}
$left = 12.5; $right = 3; $v = 100;
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
