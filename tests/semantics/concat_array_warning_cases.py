"""Native-first ordinary concatenation array warnings; outcomes are observed."""

CASES = {
    'concat-array-left-handler-write': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", ($m === "Array to string conversion"), ":", $line, ";";
    unset($GLOBALS['left']);
    $GLOBALS['right'] = "after";
    return true;
}
$left = []; $left[] = 7; $right = "before"; $v = 100;
set_error_handler("h");
try {
    $v = $left .
        $right;
    echo "R:", $v, ":", ($v === "Arrayafter"), ":", (isset($left) === false), ":", $right, ";";
} finally { echo "F;"; }
echo "END;";
''',
    'concat-array-left-handler-throw': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", ($m === "Array to string conversion"), ":", $line, ";";
    unset($GLOBALS['left']);
    $GLOBALS['right'] = "after";
    throw $GLOBALS['second'];
}
$left = []; $left[] = 7; $right = "before"; $v = 100;
$second = new Exception("second");
set_error_handler("h");
try {
    $v = $left .
        $right;
    echo "BODY;";
} catch (Throwable $e) {
    echo "C:", ($e === $second), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", (isset($left) === false), ":", $right, ";";
} finally { echo "F;"; }
echo "END;";
''',
}
