"""Two bitwise conversions preserve ordered callbacks and both saved longs."""

AND = b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":";
    if ($GLOBALS['calls'] === 1) {
        echo ($m === "Implicit conversion from float 12.5 to int loses precision"), ";";
        $GLOBALS['alias'] =& $GLOBALS['left'];
        $GLOBALS['left'] = 99;
        $GLOBALS['right'] = 5.5;
        if ($GLOBALS['throw_at'] === 1) { throw $GLOBALS['second']; }
        return true;
    }
    echo ($m === "Implicit conversion from float 5.5 to int loses precision"), ";";
    $GLOBALS['left'] = 88;
    $GLOBALS['right'] = 10;
    if ($GLOBALS['throw_at'] === 2) { throw $GLOBALS['second']; }
    return true;
}
$calls = 0; $throw_at = 0;
$left = 12.5; $right = 8.5; $v = 100;
$second = new Exception("second");
set_error_handler("h");
try {
    $v = ($left &=
        $right);
    echo "R:", $v, ":", ($v === 4), ":", $left, ":", $alias, ":", $right, ":", $calls, ";";
} catch (Throwable $e) {
    echo "C:", ($e === $second), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $left, ":", $alias, ":", $right, ":", $calls, ";";
} finally { echo "F;"; }
$left = 7;
echo "A:", $left, ":", $alias, ";END;";
'''

OR = AND.replace(b'$left &=', b'$left |=').replace(b'$v === 4', b'$v === 13')
XOR = AND.replace(b'$left &=', b'$left ^=').replace(b'$v === 4', b'$v === 9')

CASES = {
    'bitassign-both-and-handler-write': AND,
    'bitassign-both-or-handler-write': OR,
    'bitassign-both-xor-handler-write': XOR,
    'bitassign-both-and-first-throw': AND.replace(b'$throw_at = 0;', b'$throw_at = 1;'),
    'bitassign-both-xor-second-throw': XOR.replace(b'$throw_at = 0;', b'$throw_at = 2;'),
    'bitassign-both-or-first-quiet': OR.replace(b"$GLOBALS['right'] = 5.5;", b"$GLOBALS['right'] = 5;"),
}
