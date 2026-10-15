"""Independent unary-minus warning, minimum integer and default-fallback original."""
CASES = {
    'unary-minus-leading-min-default': b'''<?php
function h($n, $m, $file, $line) {
    echo 'H:', $n, ':', $m === 'A non-numeric value encountered', ':', $line, ';';
    $GLOBALS['x'] = 99;
    return false;
}
set_error_handler('h');
$x = '-9223372036854775808tail'; $v = 100;
try {
    $v = -
        $x;
    echo 'R:', $v, ':', $v === 9223372036854775808, ':', $x === 99, ';';
} finally { echo 'F;'; }
echo 'END;';
''',
}
