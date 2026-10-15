"""Native-first plain-CV concatenation assignment array warnings."""

CASES = {
    'concatassign-array-right-handler-write': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", ($m === "Array to string conversion"), ":", $line, ";";
    $GLOBALS['left'] = "after";
    unset($GLOBALS['right']);
    return true;
}
$left = "be"; $left = $left . "fore";
$right = []; $right[] = 7; $v = 100;
set_error_handler("h");
try {
    $v = ($left .=
        $right);
    echo "R:", $v, ":", ($v === "beforeArray"), ":", $left, ":", (isset($right) === false), ";";
} finally { echo "F;"; }
echo "END;";
''',
    'concatassign-array-right-handler-throw': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", ($m === "Array to string conversion"), ":", $line, ";";
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = "after";
    unset($GLOBALS['right']);
    throw $GLOBALS['second'];
}
$left = "be"; $left = $left . "fore";
$right = []; $right[] = 7; $v = 100;
$second = new Exception("second");
set_error_handler("h");
try {
    $v = ($left .=
        $right);
    echo "BODY;";
} catch (Throwable $e) {
    echo "C:", ($e === $second), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $left, ":", $alias, ":", (isset($right) === false), ";";
} finally { echo "F;"; }
$left = "later";
echo "A:", $left, ":", $alias, ";END;";
''',
}
