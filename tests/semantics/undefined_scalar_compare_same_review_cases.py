"""Shared missing-CV nonreflexivity, reference writes and warning boundary."""

CASES = {
    'peer-same-forward-equal-fresh-reference': b'''<?php
function peerSameEqual102($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ';';
    $GLOBALS['alias'] =& $GLOBALS['x'];
    $GLOBALS['x'] = '0';
    return true;
}
$result = 41;
set_error_handler('peerSameEqual102');
$result = ($x
    ==
    $x);
echo 'R:', ($result === false), ':', ($x === '0'), ':', ($alias === '0'), ';';
$alias = 5;
echo 'A:', ($x === 5), ':', ($result === false), ';END;';
''',
    'peer-same-forward-less-notequal-target-reference': b'''<?php
function peerSameTarget102($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ';';
    $GLOBALS['x'] =& $GLOBALS['target'];
    return true;
}
$target = '0'; $lt = 41; $ne = 41;
set_error_handler('peerSameTarget102');
$lt = ($x < $x);
unset($x);
$ne = ($x != $x);
echo 'R:', ($lt === true), ':', ($ne === true), ':', ($x === '0'), ':', ($target === '0'), ';';
$target = 5;
echo 'A:', ($x === 5), ':', ($lt === true), ':', ($ne === true), ';END;';
''',
    'peer-same-forward-less-equal-remains-missing-default': b'''<?php
function peerSameMissing102($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ':', $GLOBALS['calls'], ';';
    return false;
}
$calls = 0; $result = 41;
set_error_handler('peerSameMissing102');
$result = ($x <= $x);
echo 'R:', ($result === true), ':', ($calls === 2), ':', !isset($x), ';END;';
''',
    'peer-same-forward-notequal-supplied-throw': b'''<?php
function peerSameThrow102($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ';';
    throw $GLOBALS['chosen'];
}
$chosen = new Exception('selected'); $result = 41;
set_error_handler('peerSameThrow102');
try { $result = ($x != $x); echo 'BAD;'; }
catch (Exception $caught) { echo 'C:', ($caught === $chosen), ':', ($result === 41), ':', !isset($x), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
}
