"""Independent reversed both-missing originals retained byte-for-byte."""

CASES = {
    'peer-both-missing-greater-left-reference-created': b'''<?php
function peerBothLeftReference96($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    $GLOBALS['missing'] = 9;
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = '0';
    return true;
}
$result = 41;
set_error_handler('peerBothLeftReference96');
$result = ($left
    >
    $missing);
echo 'R:', ($result === true), ':', ($left === '0'), ':', ($missing === 9), ':', ($alias === '0'), ';';
$alias = 5;
echo 'A:', ($left === 5), ';END;';
''',
    'peer-both-missing-greater-equal-left-bound-to-target-reference': b'''<?php
function peerBothLeftTarget96($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    $GLOBALS['left'] =& $GLOBALS['target'];
    return true;
}
$target = 0; $result = 41;
set_error_handler('peerBothLeftTarget96');
$result = ($left >= $missing);
echo 'R:', ($result === true), ':', ($left === 0), ':', !isset($missing), ';';
$target = 5;
echo 'A:', ($left === 5), ':', ($result === true), ';END;';
''',
    'peer-both-missing-left-remains-missing': b'''<?php
function peerBothMissing96($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $left'), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    return true;
}
$result = 41;
set_error_handler('peerBothMissing96');
$result = ($left >= $missing);
echo 'R:', ($result === true), ':', !isset($left), ':', !isset($missing), ';END;';
''',
    'peer-both-missing-throw-leaves-left-missing': b'''<?php
function peerBothThrow96($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $left'), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    throw $GLOBALS['chosen'];
}
$chosen = new Exception('selected'); $result = 41;
set_error_handler('peerBothThrow96');
try { $result = ($left > $missing); echo 'BAD;'; }
catch (Exception $caught) { echo 'C:', ($caught === $chosen), ':', ($result === 41), ':', !isset($left), ':', !isset($missing), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
}
