"""ADD failure after warning mutation of stable selected referents."""
CASES = {
    'arithmetic-add-handler-invalid-right': b'''<?php
function h($n, $m, $file, $line) {
    echo 'H:', $n, ':', $m === 'A non-numeric value encountered', ':', $line, ';';
    $GLOBALS['left'] = true;
    $GLOBALS['right'] = 'notnumeric';
    return true;
}
set_error_handler('h');
$left = '12tail'; $leftAlias =& $left; $right = 2; $rightAlias =& $right; $v = 100;
try {
    $v = $left + $right;
    echo 'BAD-R;';
} catch (Throwable $e) {
    echo 'C:', $e instanceof TypeError, ':', $e->getMessage(), ':', $e->getLine(), ':', $e->getPrevious() === null, ':', $v === 100, ':', $left === true, ':', $right === 'notnumeric', ':', $leftAlias === true, ':', $rightAlias === 'notnumeric', ';';
} finally { echo 'F;'; }
echo 'END;';
''',
}
