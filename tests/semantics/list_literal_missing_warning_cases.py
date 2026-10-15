"""Pooled and temporary literal-array RHS missing-key warnings."""

CASES = {
    'list-literal-missing-pooled-result': b'''<?php
function list_literal_warning($level, $message, $file, $line) {
    echo "W:", $level, ":", ($message === "Undefined array key 0"), ":", $line, ";";
    $GLOBALS['x'] = 90;
    return true;
}
$x = 7; $y = 8; $dest = 100;
set_error_handler("list_literal_warning");
$dest = ([
    $x,
    $y
] = [
    1 => 2
]);
restore_error_handler();
echo "R:", ($x === null), ":", $y, ":", $dest[1], ":", isset($dest[0]), ";";
''',
    'list-literal-missing-reference-retire': b'''<?php
function list_literal_warning($level, $message, $file, $line) {
    echo "W:", $level, ":", ($message === "Undefined array key 0"), ":", $line, ";";
    $GLOBALS['q'] = 33;
    unset($GLOBALS['q']);
    return true;
}
$q = 2; $x = 7; $y = 8;
set_error_handler("list_literal_warning");
[$x, $y] = [1 => &$q];
restore_error_handler();
echo "R:", ($x === null), ":", $y, ":", isset($q), ";";
''',
    'list-literal-missing-reference-throw': b'''<?php
function list_literal_warning($level, $message, $file, $line) {
    echo "W:", $level, ":", ($message === "Undefined array key 0"), ":", $line, ";";
    $GLOBALS['x'] = 99;
    $GLOBALS['q'] = 33;
    unset($GLOBALS['q']);
    throw $GLOBALS['second'];
}
$q = 2; $x = 7; $y = 8; $dest = 100;
$second = new Exception("same");
set_error_handler("list_literal_warning");
try {
    $dest = ([$x, $y] = [1 => &$q]);
    echo "BODY;";
} catch (Throwable $e) {
    echo "C:", ($e === $second), ":", ($e->getPrevious() === null), ":", $x, ":", $y, ":", $dest, ";";
} finally { echo "F;"; }
restore_error_handler();
echo "R:", isset($q), ";";
''',
}
