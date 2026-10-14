"""Leading-numeric division with stable selected reference cells."""

CASES = {
    'division-leading-handler-zero': b'''<?php
function h($n, $m) {
    echo "H:", $n, ":", ($m === "A non-numeric value encountered"), ";";
    $GLOBALS["left"] = 99;
    $GLOBALS["right"] = 0;
    return true;
}
set_error_handler("h");
$left = "12tail"; $leftAlias =& $left;
$right = 2; $rightAlias =& $right; $v = 100;
try {
    $v = $left / $right;
    echo "R:", $v, ";";
} catch (DivisionByZeroError $e) {
    echo "C:", ($e->getMessage() === "Division by zero"), ":", $e->getLine(), ":",
        ($e->getPrevious() === null), ":", ($v === 100), ":",
        ($left === 99 && $leftAlias === 99), ":",
        ($right === 0 && $rightAlias === 0), ";";
} finally { echo "F;"; }
echo "END;";
''',
}
