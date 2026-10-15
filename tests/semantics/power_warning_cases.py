"""Native-first zero-base negative-exponent deprecations."""

CASES = {
    'power-zero-negative-handler-write': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", ($m === "Power of base 0 and negative exponent is deprecated"), ":", $line, ";";
    $GLOBALS['base'] = 2;
    $GLOBALS['exponent'] = 3;
    return true;
}
$base = 0; $exponent = -2; $v = 100;
set_error_handler("h");
try {
    $v = $base **
        $exponent;
    echo "R:", $v, ":", ($v === 1e999), ":", $base, ":", $exponent, ";";
} finally { echo "F;"; }
echo "END;";
''',
    'power-zero-negative-handler-throw': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", ($m === "Power of base 0 and negative exponent is deprecated"), ":", $line, ";";
    $GLOBALS['base'] = 2;
    $GLOBALS['exponent'] = 3;
    throw $GLOBALS['second'];
}
$base = 0; $exponent = -2; $v = 100;
$second = new Exception("second");
set_error_handler("h");
try {
    $v = $base **
        $exponent;
    echo "BODY;";
} catch (Throwable $e) {
    echo "C:", ($e === $second), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $base, ":", $exponent, ";";
} finally { echo "F;"; }
echo "END;";
''',
}
