"""Recursive literal RHS warnings distinguish pooled roots and runtime cells."""

CASES = {
    'list-recursive-literal-pooled-keyed': b'''<?php
function list_recursive_literal_warning($level, $message, $file, $line) {
    echo "H:", $level, ":", ($message === "Undefined array key 3"), ":", $line, ":", $GLOBALS['before'], ";";
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $GLOBALS['before'] = 21; $GLOBALS['x'] = 99;
    return false;
}
error_reporting(0);
$calls = 0; $before = 7; $x = 8; $y = 9; $nil = 10; $near = 11; $tail = 12; $dest = 100;
set_error_handler("list_recursive_literal_warning");
$dest = ([
    [["0" => $before,
      "3" => $x,
      "2" => $y,
      "4" => $nil], $near],
    $tail
] = [[[0 => 5, 2 => 6, 4 => null], 7], 8]);
restore_error_handler();
echo "R:", $before, ":", ($x === null), ":", $y, ":", ($nil === null), ":", $near, ":", $tail, ":", $dest[0][0][0], ":", $dest[0][0][2], ":", isset($dest[0][0][3]), ":", $calls, ";";
unset($dest);
''',
    'list-recursive-literal-runtime-ref-rebind': b'''<?php
function list_recursive_literal_warning($level, $message, $file, $line) {
    echo "W:", $level, ":", ($message === "Undefined array key 0"), ":", $line, ";";
    $GLOBALS['x'] = 99;
    $GLOBALS['q'] =& $GLOBALS['other'];
    $GLOBALS['q'] = 44;
    return true;
}
$q = 2; $other = 11; $x = 7; $y = 8; $near = 9; $tail = 10; $dest = 100;
set_error_handler("list_recursive_literal_warning");
$dest = ([
    [[$x, $y], $near],
    $tail
] = [[[1 => &$q], 3], 4]);
restore_error_handler();
echo "R:", ($x === null), ":", $y, ":", $near, ":", $tail, ":", $dest[0][0][1], ":", $q, ":", $other, ";";
$dest[0][0][1] = 55;
echo "A:", $y, ":", $dest[0][0][1], ":", $q, ":", $other, ";";
unset($dest, $q, $other);
echo "U:", isset($q), ";";
''',
    'list-recursive-literal-pooled-throw': b'''<?php
function list_recursive_literal_warning($level, $message, $file, $line) {
    echo "W:", $level, ":", ($message === "Undefined array key 0"), ":", $line, ":", $GLOBALS['outerbefore'], ":", $GLOBALS['midbefore'], ":", $GLOBALS['before'], ";";
    $GLOBALS['x'] = 99;
    throw $GLOBALS['second'];
}
$outerbefore = 1; $midbefore = 2; $before = 3; $x = 7; $y = 8; $near = 50; $middle = 60; $tail = 70; $dest = 100;
$second = new Exception("same");
set_error_handler("list_recursive_literal_warning");
try {
    $dest = ([
        $outerbefore,
        [$midbefore,
         [$before, [$x, $y], $near],
         $middle],
        $tail
    ] = [9, [7, [5, [1 => 2], 6], 8], 10]);
} catch (Throwable $e) {
    echo "C:", ($e === $second), ":", ($e->getPrevious() === null), ":", $outerbefore, ":", $midbefore, ":", $before, ":", $x, ":", $y, ":", $near, ":", $middle, ":", $tail, ":", $dest, ";";
} finally { echo "F;"; }
restore_error_handler();
echo "END;";
''',
}
