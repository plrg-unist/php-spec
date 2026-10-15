"""Deep by-value list warnings retain every captured array continuation."""

CASES = {
    'list-recursive-missing-depth3-snapshot': b'''<?php
function list_recursive_warning($level, $message, $file, $line) {
    echo "W:", $level, ":", ($message === "Undefined array key 0"), ":", $line, ";";
    $GLOBALS['x'] = 99; $GLOBALS['q'] = 33;
    $GLOBALS['a'] = [[[11, 22], 30], 40];
    return true;
}
$q = 2; $inner = [1 => &$q]; $mid = [$inner, 3]; $a = [$mid, 4]; unset($inner, $mid);
$x = 7; $y = 8; $near = 9; $tail = 10; $dest = 100;
set_error_handler("list_recursive_warning");
$dest = ([
    [[$x, $y], $near],
    $tail
] = $a);
restore_error_handler();
echo "R:", ($x === null), ":", $y, ":", $near, ":", $tail, ":", $dest[0][0][1], ":", $a[0][0][1], ";";
unset($dest, $a, $q);
''',
    'list-recursive-missing-depth4-keyed': b'''<?php
function list_recursive_warning($level, $message, $file, $line) {
    echo "H:", ($message === "Undefined array key 3"), ":", $line, ":", $GLOBALS['before'], ";";
    $GLOBALS['before'] = 21; $GLOBALS['x'] = 99;
    $GLOBALS['a'] = [[[[100, 200], 70], 80], 90];
    return false;
}
error_reporting(0);
$a = [[[[0 => 5, 2 => 6], 7], 8], 9];
$before = 7; $x = 8; $y = 9; $near = 10; $middle = 11; $tail = 12; $dest = 100;
set_error_handler("list_recursive_warning");
$dest = ([
    [
        [["0" => $before,
          "3" => $x,
          "2" => $y], $near],
        $middle
    ],
    $tail
] = $a);
restore_error_handler();
echo "R:", $before, ":", ($x === null), ":", $y, ":", $near, ":", $middle, ":", $tail, ":", $dest[0][0][0][0], ":", $dest[0][0][0][2], ";";
''',
    'list-recursive-missing-depth4-throw': b'''<?php
function list_recursive_warning($level, $message, $file, $line) {
    echo "W:", $level, ":", ($message === "Undefined array key 0"), ":", $line, ":", $GLOBALS['outerbefore'], ":", $GLOBALS['midbefore'], ":", $GLOBALS['before'], ";";
    $GLOBALS['x'] = 99;
    unset($GLOBALS['a'], $GLOBALS['q']);
    throw $GLOBALS['second'];
}
$q = 2; $inner = [1 => &$q]; $low = [5, $inner, 6]; $mid = [7, $low, 8]; $a = [9, $mid, 10]; unset($inner, $low, $mid);
$outerbefore = 1; $midbefore = 2; $before = 3; $x = 7; $y = 8; $near = 50; $middle = 60; $tail = 70; $dest = 100;
$second = new Exception("same");
set_error_handler("list_recursive_warning");
try {
    $dest = ([
        $outerbefore,
        [$midbefore,
         [$before, [$x, $y], $near],
         $middle],
        $tail
    ] = $a);
} catch (Throwable $e) {
    echo "C:", ($e === $second), ":", ($e->getPrevious() === null), ":", $outerbefore, ":", $midbefore, ":", $before, ":", $x, ":", $y, ":", $near, ":", $middle, ":", $tail, ":", $dest, ";";
} finally { echo "F;"; }
restore_error_handler();
echo "R:", isset($a), ":", isset($q), ";";
''',
}
