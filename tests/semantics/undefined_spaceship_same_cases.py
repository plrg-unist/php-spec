"""Same missing direct CV: frozen first NULL, current second read."""

CASES = {
    'same-spaceship-string': b'''<?php
function sameString98($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['x'] = '0';
    return true;
}
$result = 41;
set_error_handler('sameString98');

$result = ($x <=> $x);
echo 'R:', ($result === -1), ':', ($x === '0'), ':', isset($x), ';END;';
''',
    'same-spaceship-zero': b'''<?php
function sameZero98($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['x'] = 0;
    return true;
}
$result = 41;
set_error_handler('sameZero98');

$result = ($x <=> $x);
echo 'R:', ($result === 0), ':', ($x === 0), ':', isset($x), ';END;';
''',
    'same-spaceship-boolean': b'''<?php
function sameBool98($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['x'] = true; return true;
}
$result = 41;
set_error_handler('sameBool98');
$result = ($x <=> $x);
echo 'R:', ($result === -1), ':', ($x === true), ':', isset($x), ';END;';
''',
    'same-spaceship-false': b'''<?php
function sameFalse98($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ';';
    $GLOBALS['x'] = '0'; return false;
}
$result = 41;
set_error_handler('sameFalse98');
$result = ($x <=> $x);
echo 'R:', ($result === -1), ':', ($x === '0'), ':', isset($x), ';END;';
''',
    'same-spaceship-throw': b'''<?php
function sameThrow98($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ';';
    throw $GLOBALS['chosen'];
}
$result = 41; $chosen = new Exception('selected');
set_error_handler('sameThrow98');
try { $result = ($x <=> $x); echo 'BAD;'; }
catch (Exception $caught) { echo 'C:', ($caught === $chosen), ':', ($result === 41), ':', !isset($x), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
    'same-spaceship-array-boundary': b'''<?php
function sameArray98($n, $m, $file, $line) {
    echo 'H|'; $GLOBALS['x'] = []; return true;
}
$result = 41;
set_error_handler('sameArray98');
echo 'B|'; $result = ($x <=> $x); echo $result;
''',
}
