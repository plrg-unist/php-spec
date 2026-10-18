"""Quiet bool/null RHS conversion after a both-fractional LEFT warning."""

MOD = b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":";
    if ($GLOBALS['calls'] === 1) {
        echo ($m === "Implicit conversion from float 12.5 to int loses precision"), ";";
        $GLOBALS['alias'] =& $GLOBALS['left'];
        $GLOBALS['left'] = 99;
        $GLOBALS['right'] = true;
        if ($GLOBALS['throw_at'] === 1) { throw $GLOBALS['second']; }
        return true;
    }
    echo "BAD-H;";
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
    $v = ($left %=
        $right);
    echo "R:", $v, ":", ($v === 0), ":", $left, ":", $alias, ":", $right, ":", ($right === true), ":", $calls, ";";
} catch (Throwable $e) {
    echo "C:", ($e === $second), ":", ($e instanceof DivisionByZeroError), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $left, ":", $alias, ":", $right, ":", ($right === true), ":", $calls, ";";
} finally { echo "F;"; }
$left = 7;
echo "A:", $left, ":", $alias, ";END;";
'''

LEFT = MOD.replace(b'$left %=', b'$left <<=').replace(b'$v === 0', b'$v === 24')
RIGHT = MOD.replace(b'$left %=', b'$left >>=').replace(b'$v === 0', b'$v === 6')
AND = MOD.replace(b'$left %=', b'$left &=')
OR = MOD.replace(b'$left %=', b'$left |=').replace(b'$v === 0', b'$v === 13')
XOR = MOD.replace(b'$left %=', b'$left ^=').replace(b'$v === 0', b'$v === 13')

CASES = {
    'quiet-scalar-mod-true': MOD,
    'quiet-scalar-left-true': LEFT,
    'quiet-scalar-right-true': RIGHT,
    'quiet-scalar-and-true': AND,
    'quiet-scalar-or-true': OR,
    'quiet-scalar-xor-true': XOR,
    'quiet-scalar-mod-false': MOD.replace(b"$GLOBALS['right'] = true;", b"$GLOBALS['right'] = false;").replace(b'$right === true', b'$right === false'),
    'quiet-scalar-first-throw': AND.replace(b'$throw_at = 0;', b'$throw_at = 1;'),
}
