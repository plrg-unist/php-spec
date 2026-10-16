"""Nested mixed patterns distinguish saved child cells from the live root cell."""

CASES = {
    'list-nested-reference-root-replace': b'''<?php
function list_nested_reference_warning($level, $message, $file, $line) {
    echo "W:", $level, ":", ($message === "Undefined array key 0"), ":", $line, ":", $GLOBALS['q'], ";";
    $GLOBALS['x'] = 99; $GLOBALS['q'] = 33;
    $GLOBALS['a'] = [[11, 22], 40];
    return true;
}
$q = 2; $a = [[1 => &$q], 3];
$x = 7; $y = 8; $tail = 9; $dest = 100;
set_error_handler("list_nested_reference_warning");
$dest = ([
    [$x, $y],
    &$tail
] = $a);
restore_error_handler();
echo "R:", ($x === null), ":", $y, ":", $tail, ":", $dest[0][1], ":", $a[0][1], ":", $q, ";";
$y = 55; $tail = 77;
echo "A:", $y, ":", $q, ":", $dest[0][1], ":", $a[0][1], ":", $dest[1], ":", $a[1], ";";
unset($dest, $a, $q, $tail);
''',
    'list-nested-reference-root-null-descent': b'''<?php
function list_nested_reference_warning($level, $message, $file, $line) {
    echo "H:", $level, ":", ($message === "Undefined array key 0"), ":", $line, ";";
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $GLOBALS['a'] = null;
    $GLOBALS['x'] = 99; $GLOBALS['y'] = 88; $GLOBALS['z'] = 77;
    return false;
}
error_reporting(0);
$a = [1 => [0 => 5, 1 => 6]];
$x = 7; $y = 8; $z = 9; $calls = 0; $dest = 100;
set_error_handler("list_nested_reference_warning");
$dest = ([
    $x,
    [$y, &$z]
] = $a);
restore_error_handler();
echo "R:", ($x === null), ":", ($y === null), ":", ($z === null), ":", ($a[1][1] === null), ":", ($dest[1][1] === null), ":", $calls, ";";
$z = 77;
echo "A:", $z, ":", $a[1][1], ":", $dest[1][1], ";";
unset($dest, $a, $z);
''',
    'list-nested-reference-throw-cleanup': b'''<?php
function list_nested_reference_warning($level, $message, $file, $line) {
    echo "W:", $level, ":", ($message === "Undefined array key 0"), ":", $line, ":", $GLOBALS['outerbefore'], ":", $GLOBALS['before'], ";";
    $GLOBALS['x'] = 99;
    unset($GLOBALS['a'], $GLOBALS['q']);
    throw $GLOBALS['second'];
}
$q = 2; $a = [9, [5, [1 => &$q], 6], 10];
$outerbefore = 1; $before = 2; $x = 7; $y = 8; $near = 50; $tail = 70; $dest = 100;
$second = new Exception("same");
set_error_handler("list_nested_reference_warning");
try {
    $dest = ([
        $outerbefore,
        [$before,
         [$x, &$y],
         $near],
        $tail
    ] = $a);
} catch (Throwable $e) {
    echo "C:", ($e === $second), ":", ($e->getPrevious() === null), ":", $outerbefore, ":", $before, ":", $x, ":", $y, ":", $near, ":", $tail, ":", $dest, ";";
} finally { echo "F;"; }
restore_error_handler();
echo "R:", isset($a), ":", isset($q), ";";
''',
}
