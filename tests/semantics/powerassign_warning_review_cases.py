"""Signed-zero power assignment with a false deprecation handler."""

CASES = {
    'powerassign-negative-zero-default': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", ($m === "Power of base 0 and negative exponent is deprecated"), ":", $line, ";";
    $GLOBALS['base'] = 4;
    $GLOBALS['exponent'] = 2;
    return false;
}
$base = -0.0;
$exponent = -3;
$v = 100;
set_error_handler('h');
try {
    $v = ($base
        **=
        $exponent);
    echo "R:", $v, ":", ($v === -1e999), ":", $base, ":", ($base === $v), ":", $exponent, ";";
} catch (Throwable $e) {
    echo "BAD-C;";
} finally {
    echo "F;";
}
echo "END;";
''',
}
