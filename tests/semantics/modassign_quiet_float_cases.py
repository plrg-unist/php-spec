"""An integral float after LEFT deprecation converts quietly before modulo."""

NORMAL = b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":";
    if ($GLOBALS['calls'] === 1) {
        echo ($m === "Implicit conversion from float 12.5 to int loses precision"), ";";
        $GLOBALS['alias'] =& $GLOBALS['left'];
        $GLOBALS['left'] = 99;
        $GLOBALS['right'] = 5.0;
        if ($GLOBALS['throw_at'] === 1) { throw $GLOBALS['second']; }
        return true;
    }
    echo ($m === "Implicit conversion from float 5.5 to int loses precision"), ";";
    $GLOBALS['left'] = 88;
    $GLOBALS['right'] = 7;
    if ($GLOBALS['throw_at'] === 2) { throw $GLOBALS['second']; }
    return true;
}
$calls = 0; $throw_at = 0;
$left = 12.5; $right = 8.5; $v = 100;
$second = new Exception("second");
set_error_handler("h");
try {
    $v = ($left %=
        $right);
    echo "R:", $v, ":", ($v === 2), ":", $left, ":", $alias, ":", $right, ":", ($right === 5.0), ":", $calls, ";";
} catch (Throwable $e) {
    echo "C:", ($e === $second), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $left, ":", $alias, ":", $right, ":", ($right === 5.0), ":", $calls, ";";
} finally { echo "F;"; }
$left = 7;
echo "A:", $left, ":", $alias, ";END;";
'''

CASES = {
    'modassign-quiet-float-handler-write': NORMAL,
    'modassign-quiet-float-handler-throw': NORMAL.replace(b'$throw_at = 0;', b'$throw_at = 1;'),
}
