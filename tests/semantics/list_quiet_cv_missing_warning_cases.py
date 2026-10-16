"""Quiet converted CV keys are captured before missing-list callbacks."""

CASES = {
    'list-quiet-cv-bool-two-handlers': b'''<?php
function list_quiet_cv_second($level, $message, $file, $line) {
    echo "S:", $level, ":", ($message === "Undefined array key 1"), ":", $line, ":", ($GLOBALS['x'] === null), ":", $GLOBALS['y'], ";";
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $GLOBALS['key'] = false; $GLOBALS['next'] = false;
    $GLOBALS['x'] = 77; $GLOBALS['y'] = 88; $GLOBALS['a'][1] = 12;
    return false;
}
function list_quiet_cv_warning($level, $message, $file, $line) {
    echo "F:", $level, ":", ($message === "Undefined array key 0"), ":", $line, ":", ($GLOBALS['key'] === false), ":", $GLOBALS['x'], ";";
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $GLOBALS['key'] = 1.5; $GLOBALS['next'] = true;
    $GLOBALS['x'] = 99; $GLOBALS['a'][0] = 11;
    set_error_handler("list_quiet_cv_second");
    return true;
}
error_reporting(0);
$a = [2 => 22, 3 => null]; $key = false; $next = false;
$x = 7; $y = 8; $present = 9; $calls = 0; $dest = 100;
set_error_handler("list_quiet_cv_warning");
$dest = ([
    $key => $x,
    $next => $y,
    3 => $present
] = $a);
restore_error_handler();
echo "R:", ($key === false), ":", ($next === false), ":", $x, ":", ($y === null), ":", ($present === null), ":", $a[0], ":", $a[1], ":", isset($dest[0]), ":", isset($dest[1]), ":", $dest[2], ":", $calls, ";";
unset($dest, $a);
''',
    'list-quiet-cv-float-snapshot': b'''<?php
function list_quiet_cv_warning($level, $message, $file, $line) {
    echo "W:", $level, ":", ($message === "Undefined array key -2"), ":", $line, ":", ($GLOBALS['key'] === -2.0), ":", ($GLOBALS['next'] === true), ";";
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $GLOBALS['key'] = 2.5; $GLOBALS['next'] = false;
    $GLOBALS['x'] = 99; $GLOBALS['q'] = 33; $GLOBALS['a'][-2] = 55;
    return true;
}
$q = 2; $a = [0 => &$q, 1 => 11, 2 => null];
$key = -2.0; $next = true; $x = 7; $y = 8; $present = 9; $calls = 0; $dest = 100;
set_error_handler("list_quiet_cv_warning");
$dest = ([
    $key => $x,
    $next => $y,
    2 => $present
] = $a);
restore_error_handler();
echo "R:", ($x === null), ":", $y, ":", ($present === null), ":", $key, ":", ($next === false), ":", $a[-2], ":", isset($dest[-2]), ":", $dest[0], ":", $calls, ";";
$q = 44;
echo "A:", $y, ":", $dest[0], ":", $a[0], ";";
unset($dest, $a, $q);
''',
    'list-quiet-cv-string-throw': b'''<?php
function list_quiet_cv_warning($level, $message, $file, $line) {
    echo "W:", $level, ":", ($message === 'Undefined array key "gone-key"'), ":", $line, ":", $GLOBALS['before'], ";";
    $GLOBALS['key'] = "changed"; $GLOBALS['x'] = 99;
    unset($GLOBALS['key'], $GLOBALS['a'], $GLOBALS['q']);
    throw $GLOBALS['second'];
}
$prefix = "gone"; $key = $prefix . "-key";
$q = 2; $a = [0 => 9, 1 => &$q];
$before = 5; $x = 7; $y = 8; $dest = 100;
$second = new Exception("same");
set_error_handler("list_quiet_cv_warning");
try {
    $dest = ([
        0 => $before,
        $key => $x,
        1 => $y
    ] = $a);
    echo "BODY;";
} catch (Throwable $e) {
    echo "C:", ($e === $second), ":", ($e->getPrevious() === null), ":", $before, ":", $x, ":", $y, ":", $dest, ";";
} finally { echo "F;"; }
restore_error_handler();
echo "U:", isset($key), ":", isset($a), ":", isset($q), ";";
''',
}
