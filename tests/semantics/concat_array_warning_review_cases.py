"""A right-array warning preserves the converted left string across callback writes."""

CASES = {
    'concat-array-right-default-cached-left': b'''<?php
function h($n, $m, $file, $line) {
    echo 'H:', $n, ':', $m === 'Array to string conversion', ':', $line, ';';
    $GLOBALS['left'] = 'after';
    unset($GLOBALS['right']);
    return false;
}
$left = 'be'; $left = $left . 'fore';
$right = []; $right[] = 7; $v = 100;
set_error_handler('h');
try {
    $v = $left
        .
        $right;
    echo 'R:', $v, ':', $v === 'beforeArray', ':', $left, ':', isset($right) === false, ';';
} catch (Throwable $e) { echo 'BAD-C:', $e->getMessage(), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
}
