"""Native-first explicit array-to-string cast originals; outcomes are observed."""
CASES = {
    'array-string-cast-handler-write': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", ($m === "Array to string conversion"), ":", $line, ";";
    $GLOBALS['input'] = 99;
    return true;
}
$input = []; $input[] = 7; $v = 100;
set_error_handler("h");
try {
    $v = (string)$input;
    echo "R:", $v, ":", ($v === "Array"), ":", $input, ";";
} finally { echo "F;"; }
echo "END;";
''',
    'array-string-cast-handler-throw': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", ($m === "Array to string conversion"), ":", $line, ";";
    $GLOBALS['input'] = 99;
    throw $GLOBALS['second'];
}
$input = []; $input[] = 7; $v = 100;
$second = new Exception("second");
set_error_handler("h");
try {
    $v = (string)$input;
    echo "BODY;";
} catch (Throwable $e) {
    echo "C:", ($e === $second), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $input, ";";
} finally { echo "F;"; }
echo "END;";
''',
}
