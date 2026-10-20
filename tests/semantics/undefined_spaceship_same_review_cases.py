"""Independent same-CV spaceship originals retained byte-for-byte."""

CASES = {
    'peer-same-missing-spaceship-reference-created': b'''<?php
function peerSameReference98($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ';';
    $GLOBALS['alias'] =& $GLOBALS['x'];
    $GLOBALS['x'] = '0';
    return true;
}
$result = 41;
set_error_handler('peerSameReference98');
$result = ($x
    <=>
    $x);
echo 'R:', ($result === -1), ':', ($x === '0'), ':', ($alias === '0'), ';';
$alias = 5;
echo 'A:', ($x === 5), ';END;';
''',
    'peer-same-missing-spaceship-bound-to-target-reference': b'''<?php
function peerSameTarget98($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ';';
    $GLOBALS['x'] =& $GLOBALS['target'];
    return true;
}
$target = '0'; $result = 41;
set_error_handler('peerSameTarget98');
$result = ($x <=> $x);
echo 'R:', ($result === -1), ':', ($x === '0'), ';';
$target = 5;
echo 'A:', ($x === 5), ':', ($result === -1), ';END;';
''',
    'peer-same-missing-spaceship-remains-missing': b'''<?php
function peerSameMissing98($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ';';
    return true;
}
$result = 41;
set_error_handler('peerSameMissing98');
$result = ($x <=> $x);
echo 'R:', ($result === 0), ':', !isset($x), ';END;';
''',
    'peer-same-missing-spaceship-throw-leaves-missing': b'''<?php
function peerSameThrow98($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ';';
    throw $GLOBALS['chosen'];
}
$chosen = new Exception('selected'); $result = 41;
set_error_handler('peerSameThrow98');
try { $result = ($x <=> $x); echo 'BAD;'; }
catch (Exception $caught) { echo 'C:', ($caught === $chosen), ':', ($result === 41), ':', !isset($x), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
}
