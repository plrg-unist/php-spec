"""Independent both-missing originals retained byte-for-byte."""

CASES = {
    'peer-both-missing-equal-right-reference-created': b'''<?php
function peerBothReference95($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    $GLOBALS['missing'] = 9;
    $GLOBALS['alias'] =& $GLOBALS['right'];
    $GLOBALS['right'] = 0;
    return true;
}
$result = 41;
set_error_handler('peerBothReference95');
$result = ($missing
    ==
    $right);
echo 'R:', ($result === true), ':', ($missing === 9), ':', ($right === 0), ':', ($alias === 0), ';';
$alias = 5;
echo 'A:', ($right === 5), ';END;';
''',
    'peer-both-missing-less-right-bound-to-target-reference': b'''<?php
function peerBothRebind95($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    $GLOBALS['missing'] = 9;
    $GLOBALS['right'] =& $GLOBALS['target'];
    return true;
}
$target = '0'; $result = 41;
set_error_handler('peerBothRebind95');
$result = ($missing < $right);
echo 'R:', ($result === true), ':', ($right === '0'), ':', ($missing === 9), ';';
$target = 5;
echo 'A:', ($right === 5), ':', ($result === true), ';END;';
''',
    'peer-both-missing-right-remains-missing': b'''<?php
function peerBothMissing95($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $first'), ':', ($m === 'Undefined variable $second'), ':', $line, ';';
    return true;
}
$result = 41;
set_error_handler('peerBothMissing95');
$result = ($first != $second);
echo 'R:', ($result === false), ':', !isset($first), ':', !isset($second), ';END;';
''',
    'peer-both-missing-throw-leaves-right-missing': b'''<?php
function peerBothThrow95($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $first'), ':', ($m === 'Undefined variable $second'), ':', $line, ';';
    throw $GLOBALS['chosen'];
}
$chosen = new Exception('selected'); $result = 41;
set_error_handler('peerBothThrow95');
try { $result = ($first == $second); echo 'BAD;'; }
catch (Exception $caught) { echo 'C:', ($caught === $chosen), ':', ($result === 41), ':', !isset($first), ':', !isset($second), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
}
