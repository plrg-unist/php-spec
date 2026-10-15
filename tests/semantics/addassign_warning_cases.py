"""Native-first compound ADD warning/store originals; outcomes are observed."""
CASES = {
    'addassign-leading-handler-write': b'''<?php
function h($n, $m, $file, $line) {
    global $left, $right;
    echo "H:", $n, ":", ($m === "A non-numeric value encountered"), ":", $line, ";";
    $left = 99; $right = 5;
    return true;
}
set_error_handler("h");
$left = "12tail"; $leftAlias =& $left; $right = 2; $rightAlias =& $right; $v = 100;
try {
    $v = ($left += $right);
    echo "R:", $v, ":", $left, ":", $leftAlias, ":", $right, ":", $rightAlias, ";";
} finally { echo "F;"; }
echo "END;";
''',
    'addassign-leading-handler-throw': b'''<?php
function h($n, $m, $file, $line) {
    global $left, $right, $second;
    echo "H:", $n, ":", ($m === "A non-numeric value encountered"), ":", $line, ";";
    $left = 99; $right = 5;
    throw $second;
}
set_error_handler("h");
$second = new Exception("second");
$left = "12tail"; $leftAlias =& $left; $right = 2; $rightAlias =& $right; $v = 100;
try {
    $v = ($left += $right);
    echo "BODY;";
} catch (Throwable $e) {
    echo "C:", ($e === $second), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", ($left === 99), ":", ($leftAlias === 99), ":", ($right === 5), ":", ($rightAlias === 5), ";";
} finally { echo "F;"; }
echo "END;";
''',
}
