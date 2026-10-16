"""Integer CV list keys freeze one read, then evaluate later keys afresh."""

CASES = {
    'list-integer-cv-snapshot-next': b'''<?php
function list_integer_cv_warning($level, $message, $file, $line) {
    echo "W:", $level, ":", ($message === "Undefined array key 0"), ":", $line, ":", $GLOBALS['key'], ":", $GLOBALS['next'], ":", $GLOBALS['x'], ";";
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $GLOBALS['key'] = 7; $GLOBALS['next'] = 2; $GLOBALS['x'] = 99;
    $GLOBALS['a'][0] = 11; $GLOBALS['q'] = 33;
    return true;
}
$q = 2; $a = [1 => 10, 2 => &$q, 3 => null];
$key = 0; $next = 1; $x = 7; $y = 8; $present = 9; $calls = 0; $dest = 100;
set_error_handler("list_integer_cv_warning");
$dest = ([
    $key => $x,
    $next => $y,
    3 => $present
] = $a);
restore_error_handler();
echo "R:", ($x === null), ":", $y, ":", ($present === null), ":", $key, ":", $next, ":", $a[0], ":", isset($dest[0]), ":", $dest[1], ":", $dest[2], ":", $calls, ";";
$q = 55;
echo "A:", $y, ":", $dest[2], ":", $a[2], ";";
unset($dest, $a, $q);
''',
    'list-integer-cv-second-handler': b'''<?php
function list_integer_cv_second($level, $message, $file, $line) {
    echo "S:", $level, ":", ($message === "Undefined array key 5"), ":", $line, ":", ($GLOBALS['missing'] === null), ":", $GLOBALS['tail'], ";";
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $GLOBALS['key'] = 6; $GLOBALS['missing'] = 77; $GLOBALS['tail'] = 88;
    $GLOBALS['a'][5] = 12;
    return false;
}
function list_integer_cv_warning($level, $message, $file, $line) {
    echo "F:", $level, ":", ($message === "Undefined array key 4"), ":", $line, ":", $GLOBALS['key'], ":", $GLOBALS['missing'], ";";
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $GLOBALS['key'] = 2; $GLOBALS['later'] = 5; $GLOBALS['missing'] = 99;
    $GLOBALS['a'][4] = 11;
    set_error_handler("list_integer_cv_second");
    return true;
}
error_reporting(0);
$a = [0 => 4, 2 => 22]; $first = 0; $key = 9; $later = 1;
$missing = 7; $tail = 8; $calls = 0; $dest = 100;
set_error_handler("list_integer_cv_warning");
$dest = ([
    $first => $key,
    $key => $missing,
    $later => $tail
] = $a);
restore_error_handler();
echo "R:", $key, ":", $missing, ":", ($tail === null), ":", $later, ":", $a[4], ":", $a[5], ":", isset($dest[4]), ":", isset($dest[5]), ":", $dest[0], ":", $calls, ";";
unset($dest, $a);
''',
    'list-integer-cv-throw-retire': b'''<?php
function list_integer_cv_warning($level, $message, $file, $line) {
    echo "W:", $level, ":", ($message === "Undefined array key 1"), ":", $line, ":", $GLOBALS['before'], ":", $GLOBALS['key'], ";";
    $GLOBALS['key'] = 3; $GLOBALS['x'] = 99;
    unset($GLOBALS['a'], $GLOBALS['q'], $GLOBALS['key']);
    throw $GLOBALS['second'];
}
$q = 2; $a = [0 => 9, 2 => &$q];
$key = 1; $before = 5; $x = 7; $y = 8; $dest = 100;
$second = new Exception("same");
set_error_handler("list_integer_cv_warning");
try {
    $dest = ([
        0 => $before,
        $key => $x,
        2 => $y
    ] = $a);
    echo "BODY;";
} catch (Throwable $e) {
    echo "C:", ($e === $second), ":", ($e->getPrevious() === null), ":", $before, ":", $x, ":", $y, ":", $dest, ";";
} finally { echo "F;"; }
restore_error_handler();
echo "U:", isset($a), ":", isset($q), ":", isset($key), ";";
''',
}
