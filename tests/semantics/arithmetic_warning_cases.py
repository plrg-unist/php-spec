"""Scalar arithmetic conversion warnings with stable selected referents."""
CASES = {
    'arithmetic-add-leading-selected-cells': b'''<?php
function h($n, $m) {
    echo 'H:', $n, ':', $m === 'A non-numeric value encountered', ';';
    $GLOBALS['left'] = 99;
    $GLOBALS['right'] = 5;
    return true;
}
set_error_handler('h');
$left = '12tail'; $leftAlias =& $left; $right = 2; $rightAlias =& $right; $v = 100;
try {
    $v = $left + $right;
    echo 'R:', $v, ':', $left === 99, ':', $leftAlias === 99, ':', $right === 5, ':', $rightAlias === 5, ';';
} finally { echo 'F;'; }
echo 'END;';
''',
    'arithmetic-add-leading-throw': b'''<?php
function h($n, $m) {
    echo 'H:', $n, ':', $m === 'A non-numeric value encountered', ';';
    $GLOBALS['left'] = 99;
    $GLOBALS['right'] = 5;
    throw $GLOBALS['second'];
}
set_error_handler('h');
$left = '12tail'; $leftAlias =& $left; $right = 2; $rightAlias =& $right; $second = new Exception('second'); $v = 100;
try { $v = $left + $right; echo 'R;'; }
catch (Throwable $e) {
    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $v === 100, ':', $leftAlias === 99, ':', $rightAlias === 5, ';';
} finally { echo 'F;'; }
echo 'END;';
''',
}
