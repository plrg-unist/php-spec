"""Independent negative-float bitwise NOT capture and default deprecation."""

CASES = {
    'bitnot-lossy-negative-default': b'''<?php
function h($n, $m, $file, $line) {
    echo 'H:', $n, ':', $m === 'Implicit conversion from float -1.5 to int loses precision', ':', $line, ';';
    $GLOBALS['x'] = 99;
    return false;
}
set_error_handler('h');
$x = -1.5; $v = 100;
try {
    $v = ~
        $x;
    echo 'R:', $v, ':', $v === 0, ':', $x === 99, ';';
} finally { echo 'F;'; }
echo 'END;';
''',
}
