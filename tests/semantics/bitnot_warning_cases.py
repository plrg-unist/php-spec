"""Original bitwise NOT float-deprecation capture and cancellation programs."""

CASES = {
    'bitnot-float-handler-write': b'''<?php
function h($n, $m, $file, $line) {
    echo 'H:', $n, ':', $line, ':', $m === 'Implicit conversion from float 2.5 to int loses precision', ';';
    $GLOBALS['x'] = 99;
    return true;
}
set_error_handler('h');
$x = 2.5; $v = 100;
try {
    $v = ~$x;
    echo 'R:', $v === -3, ':', $v, ':', $x, ';';
} catch (Throwable $e) { echo 'BAD-C;'; }
finally { echo 'F;'; }
echo 'END;';
''',
    'bitnot-float-handler-throw': b'''<?php
function h($n, $m, $file, $line) {
    echo 'H:', $n, ':', $line, ':', $m === 'Implicit conversion from float 2.5 to int loses precision', ';';
    $GLOBALS['x'] = 99;
    throw $GLOBALS['second'];
}
$second = new Exception('second');
set_error_handler('h');
$x = 2.5; $v = 100;
try {
    $v = ~$x;
    echo 'BAD-R;';
} catch (Throwable $e) {
    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $v === 100, ':', $x === 99, ';';
} finally { echo 'F;'; }
echo 'END;';
''',
}
