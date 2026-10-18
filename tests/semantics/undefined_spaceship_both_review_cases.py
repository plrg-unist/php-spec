"""Independent both-missing spaceship originals retained byte-for-byte."""

CASES = {
    'peer-both-missing-spaceship-right-reference-created': b'''<?php
function peerBothRightReference97($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    $GLOBALS['missing'] = 9;
    $GLOBALS['alias'] =& $GLOBALS['right'];
    $GLOBALS['right'] = '0';
    return true;
}
$result = 41;
set_error_handler('peerBothRightReference97');
$result = ($missing
    <=>
    $right);
echo 'R:', ($result === -1), ':', ($missing === 9), ':', ($right === '0'), ':', ($alias === '0'), ';';
$alias = 5;
echo 'A:', ($right === 5), ';END;';
''',
    'peer-both-missing-spaceship-right-bound-to-target-reference': b'''<?php
function peerBothRightTarget97($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    $GLOBALS['right'] =& $GLOBALS['target'];
    return true;
}
$target = '0'; $result = 41;
set_error_handler('peerBothRightTarget97');
$result = ($missing <=> $right);
echo 'R:', ($result === -1), ':', ($right === '0'), ':', !isset($missing), ';';
$target = 5;
echo 'A:', ($right === 5), ':', ($result === -1), ';END;';
''',
    'peer-both-missing-spaceship-right-remains-missing': b'''<?php
function peerBothMissing97($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $first'), ':', ($m === 'Undefined variable $second'), ':', $line, ';';
    return true;
}
$result = 41;
set_error_handler('peerBothMissing97');
$result = ($first <=> $second);
echo 'R:', ($result === 0), ':', !isset($first), ':', !isset($second), ';END;';
''',
    'peer-both-missing-spaceship-throw-leaves-right-missing': b'''<?php
function peerBothThrow97($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $first'), ':', ($m === 'Undefined variable $second'), ':', $line, ';';
    throw $GLOBALS['chosen'];
}
$chosen = new Exception('selected'); $result = 41;
set_error_handler('peerBothThrow97');
try { $result = ($first <=> $second); echo 'BAD;'; }
catch (Exception $caught) { echo 'C:', ($caught === $chosen), ':', ($result === 41), ':', !isset($first), ':', !isset($second), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
}
