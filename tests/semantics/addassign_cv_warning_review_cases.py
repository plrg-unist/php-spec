"""A plain compound destination detaches a reference created by its handler."""

CASES = {
    'addassign-cv-leading-late-alias-default': b'''<?php
function h($n, $m, $file, $line) {
    echo 'H:', $n, ':', $m === 'A non-numeric value encountered', ':', $line, ';';
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = 'notnumeric';
    $GLOBALS['right'] = 5;
    return false;
}
set_error_handler('h');
$left = '12tail'; $right = 2; $v = 100;
try {
    $v = ($left +=
        $right);
    echo 'R:', $v, ':', $v === 17, ':', $left, ':', $alias, ':', $right, ';';
    $alias = 88;
    echo 'A:', $left, ':', $alias, ';';
} catch (Throwable $e) { echo 'BAD-C:', $e->getMessage(), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
}
