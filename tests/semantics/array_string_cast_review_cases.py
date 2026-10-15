"""An array CV cast keeps its fixed result after callback removal of its input."""

CASES = {
    'array-string-cast-unset-cv-default': b'''<?php
function h($n, $m, $file, $line) {
    echo 'H:', $n, ':', $m === 'Array to string conversion', ':', $line, ';';
    unset($GLOBALS['input']);
    return false;
}
set_error_handler('h');
$input = [1]; $input[] = 2; $v = 'pending';
try {
    $v = (string)
        $input;
    echo 'R:', $v, ':', $v === 'Array', ':', isset($input) === false, ';';
    $input = 'after';
    echo 'A:', $v, ':', $input, ';';
} catch (Throwable $e) { echo 'BAD-C:', $e->getMessage(), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
}
