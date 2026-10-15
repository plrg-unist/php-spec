"""Mixed flat list patterns keep a captured RHS reference cell through warnings."""

CASES = {
    'list-reference-missing-replace-value': b'''<?php
function list_reference_warning($level, $message, $file, $line) {
    echo "W:", $level, ":", ($message === "Undefined array key 0"), ":", $line, ";";
    $GLOBALS['x'] = 99;
    $GLOBALS['q'] = 33;
    $GLOBALS['a'] = [0 => 11, 1 => 22];
    return true;
}
$q = 2; $a = [1 => &$q]; $x = 7; $y = 8; $dest = 100;
set_error_handler("list_reference_warning");
$dest = ([$x, &$y] = $a);
restore_error_handler();
echo "R:", ($x === null), ":", $y, ":", $q, ":", $dest[0], ":", $dest[1], ";";
$y = 44;
echo "A:", $a[1], ":", $dest[1], ":", $q, ";";
unset($dest, $a, $y, $q);
''',
    'list-reference-missing-replace-null': b'''<?php
function list_reference_warning($level, $message, $file, $line) {
    echo "W:", $level, ":", ($message === "Undefined array key 0"), ":", $line, ";";
    $GLOBALS['x'] = 99;
    $GLOBALS['a'] = null;
    return true;
}
$a = [1 => 2]; $x = 7; $y = 8; $dest = 100;
set_error_handler("list_reference_warning");
$dest = ([$x, &$y] = $a);
restore_error_handler();
echo "R:", ($x === null), ":", ($y === null), ":", isset($a[0]), ":", ($a[1] === null), ":", ($dest[1] === null), ";";
$y = 55;
echo "A:", $a[1], ":", $dest[1], ";";
unset($dest, $a, $y);
''',
    'list-reference-missing-throw-retire': b'''<?php
function list_reference_warning($level, $message, $file, $line) {
    echo "W:", $level, ":", ($message === "Undefined array key 0"), ":", $line, ";";
    $GLOBALS['x'] = 99;
    unset($GLOBALS['a'], $GLOBALS['q']);
    throw $GLOBALS['second'];
}
$q = 2; $a = [1 => &$q]; $x = 7; $y = 8; $dest = 100;
$second = new Exception("same");
set_error_handler("list_reference_warning");
try {
    $dest = ([$x, &$y] = $a);
    echo "BODY;";
} catch (Throwable $e) {
    echo "C:", ($e === $second), ":", ($e->getPrevious() === null), ":", $x, ":", $y, ":", $dest, ";";
} finally { echo "F;"; }
restore_error_handler();
echo "R:", isset($a), ":", isset($q), ";";
''',
}
