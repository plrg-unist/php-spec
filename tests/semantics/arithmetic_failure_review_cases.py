"""Historical numeric holders survive invalid live operands after a second warning."""

CASES = {
    'arithmetic-add-cached-right-invalid-live': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['hits'] = $GLOBALS['hits'] + 1;
    echo 'H:', $GLOBALS['hits'], ':', $n, ':', $m === 'A non-numeric value encountered', ':', $line, ';';
    if ($GLOBALS['hits'] === 1) {
        $GLOBALS['right'] = '5tail';
        return true;
    }
    $GLOBALS['left'] = true;
    $GLOBALS['right'] = 'notnumeric';
    return false;
}
set_error_handler('h');
$hits = 0;
$left = '12tail'; $leftAlias =& $left; $right = 2; $rightAlias =& $right; $v = 100;
try {
    $v = $left +
        $right;
    echo 'R:', $v, ':', $v === 17, ':', $left === true, ':', $right === 'notnumeric', ':',
        $leftAlias === true, ':', $rightAlias === 'notnumeric', ':', $hits === 2, ';';
} catch (TypeError $e) { echo 'BAD-C:', $e->getMessage(), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
}
