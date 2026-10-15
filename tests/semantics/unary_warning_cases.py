"""Unary numeric warnings with a plain defined CV and named handler."""

CASES = {
    'unary-plus-leading-handler-write': b'''<?php
function h($n, $m, $f, $line) {
    echo "H:", $n, ":", $line, ":", ($m === "A non-numeric value encountered"), ";";
    $GLOBALS["x"] = 99;
    return true;
}
set_error_handler("h");
$x = "12tail"; $v = 100;
try {
    $v = +$x;
    echo "R:", ($v === 12), ":", $v, ":", $x, ";";
} catch (Throwable $e) { echo "BAD-C;"; }
finally { echo "F;"; }
echo "END;";
''',
    'unary-minus-leading-handler-throw': b'''<?php
$second = new Exception("supplied");
function h($n, $m, $f, $line) {
    echo "H:", $n, ":", $line, ":", ($m === "A non-numeric value encountered"), ";";
    $GLOBALS["x"] = 99;
    throw $GLOBALS["second"];
}
set_error_handler("h");
$x = "12tail"; $v = 100;
try {
    $v = -$x;
    echo "BAD-R;";
} catch (Exception $e) {
    echo "C:", ($e === $second), ":", ($e->getPrevious() === null), ":",
        ($v === 100), ":", ($x === 99), ";";
} finally { echo "F;"; }
echo "END;";
''',
}
