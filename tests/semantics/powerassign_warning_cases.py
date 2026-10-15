"""Native-first power assignment deprecation and pending-exception stores."""

CASES = {
    'powerassign-zero-negative-handler-write': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", ($m === "Power of base 0 and negative exponent is deprecated"), ":", $line, ";";
    $GLOBALS['base'] = 2;
    $GLOBALS['exponent'] = 3;
    return true;
}
$base = 0; $exponent = -2; $v = 100;
set_error_handler("h");
try {
    $v = ($base **=
        $exponent);
    echo "R:", $v, ":", ($v === 1e999), ":", $base, ":", ($base === $v), ":", $exponent, ";";
} finally { echo "F;"; }
echo "END;";
''',
    'powerassign-zero-negative-handler-throw': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", ($m === "Power of base 0 and negative exponent is deprecated"), ":", $line, ";";
    $GLOBALS['alias'] =& $GLOBALS['base'];
    $GLOBALS['base'] = 2;
    $GLOBALS['exponent'] = 3;
    throw $GLOBALS['second'];
}
$base = 0; $exponent = -2; $v = 100;
$second = new Exception("second");
set_error_handler("h");
try {
    $v = ($base **=
        $exponent);
    echo "BODY;";
} catch (Throwable $e) {
    echo "C:", ($e === $second), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $base, ":", ($base === 1e999), ":", $alias, ":", $exponent, ";";
    $base = 7;
    echo "A:", $base, ":", $alias, ";";
} finally { echo "F;"; }
echo "END;";
''',
}
