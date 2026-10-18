"""Quiet complete numeric strings after a both-fractional LEFT warning."""

MOD = b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":";
    if ($GLOBALS['calls'] === 1) {
        echo ($m === "Implicit conversion from float 12.5 to int loses precision"), ";";
        $GLOBALS['alias'] =& $GLOBALS['left'];
        $GLOBALS['left'] = 99;
        $GLOBALS['right'] = '0' . $GLOBALS['tail'];
        if ($GLOBALS['throw_at'] === 1) { throw $GLOBALS['second']; }
        return true;
    }
    echo "BAD-H;";
    $GLOBALS['left'] = 88;
    $GLOBALS['right'] = 10;
    if ($GLOBALS['throw_at'] === 2) { throw $GLOBALS['second']; }
    return true;
}
$calls = 0; $throw_at = 0; $tail = 5;
$left = 12.5; $right = 8.5; $v = 100;
$second = new Exception("second");
set_error_handler("h");
try {
    $v = ($left %=
        $right);
    echo "R:", $v, ":", ($v === 2), ":", $left, ":", $alias, ":", $right, ":", ($right === "05"), ":", $calls, ";";
} catch (Throwable $e) {
    echo "C:", ($e === $second), ":", ($e instanceof DivisionByZeroError), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $left, ":", $alias, ":", $right, ":", ($right === "05"), ":", $calls, ";";
} finally { echo "F;"; }
$left = 7;
echo "A:", $left, ":", $alias, ";END;";
'''

LITERAL = MOD.replace(b"'0' . $GLOBALS['tail']", b'"5"').replace(b'$right === "05"', b'$right === "5"')
LEFT = LITERAL.replace(b'$left %=', b'$left <<=').replace(b'$v === 2', b'$v === 384')
RIGHT = LITERAL.replace(b'$left %=', b'$left >>=').replace(b'$v === 2', b'$v === 0')
AND = LITERAL.replace(b'$left %=', b'$left &=').replace(b'$v === 2', b'$v === 4')
OR = LITERAL.replace(b'$left %=', b'$left |=').replace(b'$v === 2', b'$v === 13').replace(b'"5"', b'" +5e0 "')
XOR = LITERAL.replace(b'$left %=', b'$left ^=').replace(b'$v === 2', b'$v === 9')

CASES = {
    'quiet-string-mod-carrier': MOD,
    'quiet-string-left-literal': LEFT,
    'quiet-string-right-literal': RIGHT,
    'quiet-string-and-literal': AND,
    'quiet-string-or-exponent': OR,
    'quiet-string-xor-literal': XOR,
    'quiet-string-first-throw': MOD.replace(b'$throw_at = 0;', b'$throw_at = 1;'),
}
