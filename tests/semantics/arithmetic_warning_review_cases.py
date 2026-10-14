"""Independent right-conversion warning and default-fallback original."""
CASES = {
    'arithmetic-add-leading-right-warning-fallback': b'''<?php
function h($n, $m) {
    $GLOBALS['hits'] = $GLOBALS['hits'] + 1;
    echo 'H:', $GLOBALS['hits'], ':', $n, ':', $m === 'A non-numeric value encountered', ';';
    $GLOBALS['left'] = 99;
    if ($GLOBALS['hits'] === 1) {
        $GLOBALS['right'] = '5tail';
        return true;
    }
    $GLOBALS['right'] = 7;
    return false;
}
set_error_handler('h');
$hits = 0;
$left = '12tail'; $leftAlias =& $left; $right = 2; $rightAlias =& $right; $v = 100;
try {
    $v = $left + $right;
    echo 'R:', $v, ':', $left === 99, ':', $leftAlias === 99, ':', $right === 7, ':', $rightAlias === 7, ':', $hits === 2, ';';
} finally { echo 'F;'; }
echo 'END;';
''',
}
