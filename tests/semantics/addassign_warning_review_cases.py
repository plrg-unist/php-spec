"""Compound ADD keeps its selected destination after callback name rebinding."""

CASES = {
    'addassign-leading-rebound-target-default': b'''<?php
function h($n, $m, $file, $line) {
    echo 'H:', $n, ':', $m === 'A non-numeric value encountered', ':', $line, ';';
    unset($GLOBALS['left']);
    $GLOBALS['left'] = 99;
    $GLOBALS['right'] = 5;
    return false;
}
set_error_handler('h');
$left = '12tail'; $leftAlias =& $left; $right = 2; $rightAlias =& $right; $v = 100;
try {
    $v = ($left +=
        $right);
    echo 'R:', $v, ':', $v === 17, ':', $left, ':', $leftAlias, ':',
        $right, ':', $rightAlias, ';';
} catch (Throwable $e) { echo 'BAD-C:', $e->getMessage(), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
}
