"""Quiet CV keys on pooled and runtime by-value literal roots."""

CASES = {
    'list-literal-cv-pooled-two-handlers': b'''<?php
function list_literal_cv_second($level, $message, $file, $line) {
    echo "S:", $level, ":", ($message === "Undefined array key 1"), ":", $line, ":", ($GLOBALS['x'] === null), ":", $GLOBALS['y'], ";";
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $GLOBALS['key'] = 2.5; $GLOBALS['next'] = 2.5;
    $GLOBALS['x'] = 77; $GLOBALS['y'] = 88; $GLOBALS['dest'] = 200;
    return false;
}
function list_literal_cv_warning($level, $message, $file, $line) {
    echo "F:", $level, ":", ($message === "Undefined array key 0"), ":", $line, ":", $GLOBALS['x'], ";";
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $GLOBALS['key'] = 1.5; $GLOBALS['next'] = true;
    $GLOBALS['x'] = 99; $GLOBALS['dest'] = 150;
    set_error_handler("list_literal_cv_second");
    return true;
}
error_reporting(0);
$key = false; $next = false; $x = 7; $y = 8; $present = 9; $calls = 0; $dest = 100;
set_error_handler("list_literal_cv_warning");
$dest = ([
    $key => $x,
    $next => $y,
    3 => $present
] = [2 => 22, 3 => null]);
restore_error_handler();
echo "R:", $x, ":", ($y === null), ":", ($present === null), ":", $dest[2], ":", ($dest[3] === null), ":", isset($dest[0]), ":", isset($dest[1]), ":", $calls, ";";
unset($dest);
''',
    'list-literal-cv-runtime-reference': b'''<?php
function list_literal_cv_warning($level, $message, $file, $line) {
    echo "W:", $level, ":", ($message === 'Undefined array key "lost-key"'), ":", $line, ":", $GLOBALS['q'], ";";
    $GLOBALS['x'] = 99; $GLOBALS['next'] = true;
    unset($GLOBALS['key']);
    $GLOBALS['q'] =& $GLOBALS['other']; $GLOBALS['q'] = 44;
    return true;
}
$prefix = "lost"; $key = $prefix . "-key";
$q = 2; $other = 9; $next = false; $x = 7; $y = 8; $present = 9; $dest = 100;
set_error_handler("list_literal_cv_warning");
$dest = ([
    $key => $x,
    $next => $y,
    2 => $present
] = [1 => &$q, 2 => null]);
restore_error_handler();
echo "R:", ($x === null), ":", $y, ":", ($present === null), ":", $dest[1], ":", $q, ":", $other, ":", isset($key), ";";
$dest[1] = 55;
echo "A:", $y, ":", $dest[1], ":", $q, ":", $other, ";";
unset($dest, $q, $other);
echo "U:", isset($dest), ":", isset($q), ":", isset($other), ";";
''',
    'list-literal-cv-recursive-pooled-throw': b'''<?php
function list_literal_cv_warning($level, $message, $file, $line) {
    echo "W:", $level, ":", ($message === "Undefined array key 0"), ":", $line, ":", $GLOBALS['outerbefore'], ":", $GLOBALS['before'], ";";
    $GLOBALS['x'] = 99;
    unset($GLOBALS['outer'], $GLOBALS['middle'], $GLOBALS['key']);
    throw $GLOBALS['second'];
}
$outer = 1; $middle = 1; $key = false;
$outerbefore = 1; $before = 2; $x = 7; $y = 8; $near = 50; $tail = 70; $dest = 100;
$second = new Exception("same");
set_error_handler("list_literal_cv_warning");
try {
    $dest = ([
        0 => $outerbefore,
        $outer => [
            0 => $before,
            $middle => [$key => $x, 1 => $y],
            2 => $near
        ],
        2 => $tail
    ] = [9, [5, [1 => 2], 6], 10]);
} catch (Throwable $e) {
    echo "C:", ($e === $second), ":", ($e->getPrevious() === null), ":", $outerbefore, ":", $before, ":", $x, ":", $y, ":", $near, ":", $tail, ":", $dest, ";";
} finally { echo "F;"; }
restore_error_handler();
echo "U:", isset($outer), ":", isset($middle), ":", isset($key), ";";
''',
}

REJECTIONS = {
    'list-literal-cv-mixed-rejection': b'''<?php
$key = 0;
[$key => &$x] = [1 => 2];
echo "UNREACHABLE;";
''',
}
EXIT_CODES = {'list-literal-cv-mixed-rejection': 255}
STATUSES = {'list-literal-cv-mixed-rejection': 'static_rejection'}
