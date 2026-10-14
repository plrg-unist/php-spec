"""Independent cached-zero division warning and default-fallback original."""
CASES = {
    'division-leading-right-cached-zero-fallback': b'''<?php
function h($n, $m) {
    $GLOBALS['hits'] = $GLOBALS['hits'] + 1;
    echo 'H:', $GLOBALS['hits'], ':', $n, ':', $m === 'A non-numeric value encountered', ';';
    $GLOBALS['left'] = 99;
    if ($GLOBALS['hits'] === 1) {
        $GLOBALS['right'] = '0tail';
        return true;
    }
    $GLOBALS['right'] = 7;
    return false;
}
set_error_handler('h');
$hits = 0;
$left = '12tail'; $leftAlias =& $left; $right = 2; $rightAlias =& $right; $v = 100;
try {
    $v = $left / $right;
    echo 'BAD;';
} catch (Throwable $e) {
    echo 'C:', $e instanceof DivisionByZeroError, ':', $e->getMessage(), ':', $e->getLine(), ':', $e->getPrevious() === null, ':', $v === 100, ':', $left === 99, ':', $leftAlias === 99, ':', $right === 7, ':', $rightAlias === 7, ':', $hits === 2, ';';
} finally { echo 'F;'; }
echo 'END;';
''',
}
