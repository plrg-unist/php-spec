"""Recursive quiet CV keys keep historical ancestors and fresh later reads."""

CASES = {
    'list-recursive-cv-depth3-snapshot': b'''<?php
function list_recursive_cv_warning($level, $message, $file, $line) {
    echo "W:", $level, ":", ($message === "Undefined array key 0"), ":", $line, ";";
    $GLOBALS['outer'] = null; $GLOBALS['middle'] = 1.5;
    $GLOBALS['key'] = 1.5; $GLOBALS['next'] = "1";
    $GLOBALS['x'] = 99; $GLOBALS['q'] = 33;
    unset($GLOBALS['q']);
    $GLOBALS['a'] = [[[11, 22], 30], 40];
    return true;
}
$q = 2; $inner = [1 => &$q]; $mid = [$inner, 3]; $a = [$mid, 4]; unset($inner, $mid);
$outer = 0; $middle = false; $key = false; $next = false;
$x = 7; $y = 8; $near = 9; $tail = 10; $dest = 100;
set_error_handler("list_recursive_cv_warning");
$dest = ([
    $outer => [
        $middle => [$key => $x, $next => $y],
        1 => $near
    ],
    1 => $tail
] = $a);
restore_error_handler();
echo "R:", ($x === null), ":", $y, ":", $near, ":", $tail, ":", $dest[0][0][1], ":", $a[0][0][1], ":", isset($q), ":", ($outer === null), ":", $middle, ":", $key, ";";
unset($dest, $a);
''',
    'list-recursive-cv-ancestor-null': b'''<?php
function list_recursive_cv_warning($level, $message, $file, $line) {
    echo "H:", $level, ":", ($message === "Undefined array key 0"), ":", $line, ";";
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $GLOBALS['outer'] = 1.5; $GLOBALS['middle'] = 2.5;
    $GLOBALS['tailkey'] = true;
    $GLOBALS['x'] = 99; $GLOBALS['y'] = 88;
    $GLOBALS['a'][0] = [[11, 22]];
    $GLOBALS['a'] = [0 => [[33, 44]], 1 => 40];
    return false;
}
error_reporting(0);
$a = [1 => 3]; $outer = false; $middle = 0; $tailkey = false;
$x = 7; $y = 8; $tail = 9; $calls = 0; $dest = 100;
set_error_handler("list_recursive_cv_warning");
$dest = ([
    $outer => [$middle => [$x, $y]],
    $tailkey => $tail
] = $a);
restore_error_handler();
echo "R:", ($x === null), ":", ($y === null), ":", $tail, ":", $dest[1], ":", isset($dest[0]), ":", $a[0][0][0], ":", $a[1], ":", $calls, ";";
unset($dest, $a);
''',
    'list-recursive-cv-depth3-throw': b'''<?php
function list_recursive_cv_warning($level, $message, $file, $line) {
    echo "W:", $level, ":", ($message === 'Undefined array key "gone"'), ":", $line, ":", $GLOBALS['outerbefore'], ":", $GLOBALS['before'], ";";
    $GLOBALS['x'] = 99;
    unset($GLOBALS['outer'], $GLOBALS['middle'], $GLOBALS['key'], $GLOBALS['a'], $GLOBALS['q']);
    throw $GLOBALS['second'];
}
$q = 2; $a = [9, [5, [1 => &$q], 6], 10];
$outer = 1; $middle = 1; $key = "gone";
$outerbefore = 1; $before = 2; $x = 7; $y = 8; $near = 50; $tail = 70; $dest = 100;
$second = new Exception("same");
set_error_handler("list_recursive_cv_warning");
try {
    $dest = ([
        0 => $outerbefore,
        $outer => [
            0 => $before,
            $middle => [$key => $x, 1 => &$y],
            2 => $near
        ],
        2 => $tail
    ] = $a);
} catch (Throwable $e) {
    echo "C:", ($e === $second), ":", ($e->getPrevious() === null), ":", $outerbefore, ":", $before, ":", $x, ":", $y, ":", $near, ":", $tail, ":", $dest, ";";
} finally { echo "F;"; }
restore_error_handler();
echo "U:", isset($outer), ":", isset($middle), ":", isset($key), ":", isset($a), ":", isset($q), ";";
''',
}
