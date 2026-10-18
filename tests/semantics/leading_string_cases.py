"""Ordered LEFT deprecation and leading-numeric RHS warning in compound writes."""

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
    echo ($m === "A non-numeric value encountered"), ";";
    $GLOBALS['left'] = 88;
    $GLOBALS['right'] = 7;
    if ($GLOBALS['throw_at'] === 2) { throw $GLOBALS['second']; }
    return true;
}
$calls = 0; $throw_at = 0; $tail = '5tail';
$left = 12.5; $right = 8.5; $v = 100;
$second = new Exception("second");
set_error_handler("h");
try {
    $v = ($left %=
        $right);
    echo "R:", $v, ":", ($v === 2), ":", $left, ":", $alias, ":", $right, ":", $calls, ";";
} catch (Throwable $e) {
    echo "C:", ($e === $second), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $left, ":", $alias, ":", $right, ":", $calls, ";";
} finally { echo "F;"; }
$left = 7;
echo "A:", $left, ":", $alias, ";END;";
'''

LITERAL = MOD.replace(b"'0' . $GLOBALS['tail']", b'"5tail"').replace(b"$GLOBALS['right'] = 7;", b"$GLOBALS['right'] = 10;")
LEFT = LITERAL.replace(b'$left %=', b'$left <<=').replace(b'$v === 2', b'$v === 384')
RIGHT = LITERAL.replace(b'$left %=', b'$left >>=').replace(b'$v === 2', b'$v === 0').replace(b"$GLOBALS['right'] = 10;", b"$GLOBALS['right'] = 1;")
AND = LITERAL.replace(b'$left %=', b'$left &=').replace(b'$v === 2', b'$v === 4')
OR = LITERAL.replace(b'$left %=', b'$left |=').replace(b'$v === 2', b'$v === 13').replace(b'"5tail"', b'" +5e0 tail"')
XOR = LITERAL.replace(b'$left %=', b'$left ^=').replace(b'$v === 2', b'$v === 9')

CASES = {
    'leading-string-mod-carrier': MOD,
    'leading-string-left-literal': LEFT,
    'leading-string-right-literal': RIGHT,
    'leading-string-and-literal': AND,
    'leading-string-or-exponent': OR,
    'leading-string-xor-literal': XOR,
    'leading-string-first-throw': MOD.replace(b'$throw_at = 0;', b'$throw_at = 1;'),
    'leading-string-second-throw': MOD.replace(b'$throw_at = 0;', b'$throw_at = 2;'),
}
