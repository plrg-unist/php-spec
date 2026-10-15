"""Plain-CV concat assignment with a late alias and false warning handler."""

CASES = {
    'concatassign-array-right-late-alias-default': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", ($m === "Array to string conversion"), ":", $line, ";";
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = 'after';
    unset($GLOBALS['right']);
    return false;
}
$left = 'be';
$left = $left . 'fore';
$right = [];
$right[] = 7;
$v = 100;
set_error_handler('h');
try {
    $v = ($left
        .=
        $right);
    echo "R:", $v, ":", ($v === 'beforeArray'), ":", $left, ":", $alias, ":", (!isset($right)), ";";
    $left = 'later';
    echo "A:", $left, ":", $alias, ";";
} catch (Throwable $e) {
    echo "BAD-C;";
} finally {
    echo "F;";
}
echo "END;";
''',
}
