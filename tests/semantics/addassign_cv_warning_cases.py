"""Native-first plain-CV compound ADD and late-alias originals; outcomes are observed."""
CASES = {
    'addassign-cv-leading-late-alias-write': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", ($m === "A non-numeric value encountered"), ":", $line, ";";
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = 99; $GLOBALS['right'] = 5;
    return true;
}
$left = "12tail"; $right = 2; $alias = 0; $v = 100;
set_error_handler("h");
try {
    $v = ($left += $right);
    echo "R:", $v, ":", $left, ":", $alias, ":", $right, ";";
    $left = 73;
    echo "A:", $left, ":", $alias, ";";
} finally { echo "F;"; }
echo "END;";
''',
    'addassign-cv-leading-late-alias-throw': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", ($m === "A non-numeric value encountered"), ":", $line, ";";
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = 99; $GLOBALS['right'] = 5;
    throw $GLOBALS['second'];
}
$left = "12tail"; $right = 2; $alias = 0; $v = 100;
$second = new Exception("second");
set_error_handler("h");
try {
    $v = ($left += $right);
    echo "BODY;";
} catch (Throwable $e) {
    echo "C:", ($e === $second), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $left, ":", $alias, ":", $right, ";";
    $left = 73;
    echo "A:", $left, ":", $alias, ";";
} finally { echo "F;"; }
echo "END;";
''',
}
