"""Reversed same-CV originals frozen before entry/chain implementation."""

CASES = {
    'peer-same-reversed-greater-fresh-reference': b'''<?php
function peerSameReversedEntry104($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ':', $GLOBALS['calls'], ';';
    if ($GLOBALS['calls'] === 1) {
        $GLOBALS['alias'] =& $GLOBALS['x'];
        $GLOBALS['x'] = '0';
    }
    return true;
}
$calls = 0; $result = 41;
set_error_handler('peerSameReversedEntry104');
$result = ($x
    >
    $x);
echo 'R:', ($result === true), ':', ($x === '0'), ':', ($alias === '0'), ':', ($calls === 1), ';';
$alias = 5;
echo 'A:', ($x === 5), ':', ($result === true), ';END;';
''',
    'peer-same-reversed-greater-second-target-reference-default': b'''<?php
function peerSameReversedTarget104($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ':', $GLOBALS['calls'], ';';
    if ($GLOBALS['calls'] === 1) {
        $GLOBALS['x'] = 9;
        unset($GLOBALS['x']);
    } else {
        $GLOBALS['x'] =& $GLOBALS['target'];
    }
    return false;
}
$calls = 0; $target = '0'; $result = 41;
set_error_handler('peerSameReversedTarget104');
$result = ($x > $x);
echo 'R:', ($result === false), ':', ($x === '0'), ':', ($calls === 2), ';';
$target = 5;
echo 'A:', ($x === 5), ':', ($result === false), ';END;';
''',
    'peer-same-reversed-greater-equal-entry-and-remain-missing': b'''<?php
function peerSameReversedMissing104($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ':', $GLOBALS['calls'], ';';
    if ($GLOBALS['calls'] === 1) { $GLOBALS['x'] = '0'; }
    return true;
}
$calls = 0; $first = 41; $second = 41;
set_error_handler('peerSameReversedMissing104');
$first = ($x >= $x);
unset($x);
$second = ($x >= $x);
echo 'R:', ($first === true), ':', ($second === true), ':', !isset($x), ':', ($calls === 3), ';END;';
''',
    'peer-same-reversed-greater-equal-second-supplied-throw': b'''<?php
function peerSameReversedThrow104($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ':', $GLOBALS['calls'], ';';
    if ($GLOBALS['calls'] === 2) { throw $GLOBALS['chosen']; }
    return true;
}
$calls = 0; $chosen = new Exception('selected'); $result = 41;
set_error_handler('peerSameReversedThrow104');
try { $result = ($x >= $x); echo 'BAD;'; }
catch (Exception $caught) { echo 'C:', ($caught === $chosen), ':', ($result === 41), ':', !isset($x), ':', ($calls === 2), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
}
