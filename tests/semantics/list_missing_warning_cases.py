"""Captured direct-CV destructuring arrays across missing-key handlers."""

CASES = {
    'list-missing-rebind-snapshot': b'''<?php
function list_warning($level, $message, $file, $line) {
    echo "W:", $level, ":", ($message === "Undefined array key 0"), ":", $line, ";";
    $GLOBALS['a'] = [0 => 11, 1 => 22];
    return true;
}
$a = [1 => 2]; $x = 7; $y = 8;
set_error_handler("list_warning");
$v = ([
    $x,
    $y
] =
    $a);
restore_error_handler();
echo "R:", ($x === null), ":", $y, ":", $a[0], ":", $a[1], ":", $v[1], ":", isset($v[0]), ";";
''',
    'list-missing-shared-cell-retirement': b'''<?php
function list_warning($level, $message, $file, $line) {
    echo "W:", $level, ":", ($message === "Undefined array key 0"), ":", $line, ";";
    $GLOBALS['a'][0] = 11;
    $GLOBALS['q'] = 33;
    unset($GLOBALS['a'], $GLOBALS['q']);
    return true;
}
$q = 2; $a = [1 => &$q]; $x = 7; $y = 8;
set_error_handler("list_warning");
[$x, $y] = $a;
restore_error_handler();
echo "R:", ($x === null), ":", $y, ":", isset($a), ":", isset($q), ";";
''',
    'list-missing-throw-targets': b'''<?php
function list_warning($level, $message, $file, $line) {
    echo "W:", $level, ":", ($message === "Undefined array key 0"), ":", $line, ";";
    $GLOBALS['a'][0] = 11;
    $GLOBALS['x'] = 99;
    $GLOBALS['q'] = 33;
    unset($GLOBALS['a'], $GLOBALS['q']);
    throw $GLOBALS['second'];
}
$second = new Exception("kept");
$q = 2; $a = [1 => &$q]; $x = 7; $y = 8; $v = 100;
set_error_handler("list_warning");
try {
    $v = ([$x, $y] = $a);
    echo "BODY;";
} catch (Throwable $e) {
    echo "C:", ($e === $second), ":", ($e->getPrevious() === null), ":", $x, ":", $y, ":", $v, ";";
} finally { echo "F;"; }
restore_error_handler();
echo "R:", isset($a), ":", isset($q), ";";
''',
}
