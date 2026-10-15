"""One-level by-value list warnings retain inner and outer array snapshots."""

CASES = {
    'list-nested-missing-inner-snapshot': b'''<?php
function list_nested_warning($level, $message, $file, $line) {
    echo "W:", $level, ":", ($message === "Undefined array key 0"), ":", $line, ";";
    $GLOBALS['x'] = 99;
    $GLOBALS['q'] = 33;
    $GLOBALS['a'] = [[11, 22], 44];
    return true;
}
$q = 2; $inner = [1 => &$q]; $a = [$inner, 3]; unset($inner);
$x = 7; $y = 8; $tail = 9; $dest = 100;
set_error_handler("list_nested_warning");
$dest = ([
    [$x, $y],
    $tail
] = $a);
restore_error_handler();
echo "R:", ($x === null), ":", $y, ":", $tail, ":", $dest[0][1], ":", $a[0][1], ";";
unset($dest, $a, $q);
''',
    'list-nested-missing-inner-keyed': b'''<?php
function list_nested_warning($level, $message, $file, $line) {
    echo "H:", ($message === "Undefined array key 3"), ":", $line, ":", $GLOBALS['before'], ";";
    $GLOBALS['before'] = 21;
    $GLOBALS['x'] = 99;
    $GLOBALS['a'] = [[100, 200], 400];
    return false;
}
error_reporting(0);
$a = [[0 => 5, 2 => 6], 4]; $before = 7; $x = 8; $y = 9; $tail = 10; $dest = 100;
set_error_handler("list_nested_warning");
$dest = ([
    ["0" => $before,
     "3" => $x,
     "2" => $y],
    $tail
] = $a);
restore_error_handler();
echo "R:", $before, ":", ($x === null), ":", $y, ":", $tail, ":", $dest[0][0], ":", $dest[0][2], ";";
''',
    'list-nested-missing-inner-throw': b'''<?php
function list_nested_warning($level, $message, $file, $line) {
    echo "W:", $level, ":", ($message === "Undefined array key 0"), ":", $line, ":", $GLOBALS['before'], ";";
    $GLOBALS['x'] = 99;
    unset($GLOBALS['a'], $GLOBALS['q']);
    throw $GLOBALS['second'];
}
$q = 2; $inner = [1 => &$q]; $a = [5, $inner, 3]; unset($inner);
$before = 6; $x = 7; $y = 8; $tail = 9; $dest = 100;
$second = new Exception("same");
set_error_handler("list_nested_warning");
try {
    $dest = ([
        $before,
        [$x, $y],
        $tail
    ] = $a);
} catch (Throwable $e) {
    echo "C:", ($e === $second), ":", ($e->getPrevious() === null), ":", $before, ":", $x, ":", $y, ":", $tail, ":", $dest, ";";
} finally { echo "F;"; }
restore_error_handler();
echo "R:", isset($a), ":", isset($q), ";";
''',
}
