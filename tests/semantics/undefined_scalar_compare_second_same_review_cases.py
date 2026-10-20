"""Same-CV originals frozen before second-Warning implementation."""

CASES = {
    'peer-same-second-equal-fresh-reference': b'''<?php
function peerSameSecondEqual103($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ':', $GLOBALS['calls'], ';';
    if ($GLOBALS['calls'] === 2) {
        $GLOBALS['alias'] =& $GLOBALS['x'];
        $GLOBALS['x'] = '0';
    }
    return true;
}
$calls = 0; $result = 41;
set_error_handler('peerSameSecondEqual103');
$result = ($x
    ==
    $x);
echo 'R:', ($result === true), ':', ($x === '0'), ':', ($alias === '0'), ':', ($calls === 2), ';';
$alias = 5;
echo 'A:', ($x === 5), ':', ($result === true), ';END;';
''',
    'peer-same-second-less-target-reference-default': b'''<?php
function peerSameSecondTarget103($n, $m, $file, $line) {
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
set_error_handler('peerSameSecondTarget103');
$result = ($x < $x);
echo 'R:', ($result === false), ':', ($x === '0'), ':', ($calls === 2), ';';
$target = 5;
echo 'A:', ($x === 5), ':', ($result === false), ';END;';
''',
    'peer-same-second-notequal-less-equal-remain-missing': b'''<?php
function peerSameSecondMissing103($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ':', $GLOBALS['calls'], ';';
    return true;
}
$calls = 0; $ne = 41; $le = 41;
set_error_handler('peerSameSecondMissing103');
$ne = ($x != $x);
$le = ($x <= $x);
echo 'R:', ($ne === false), ':', ($le === true), ':', !isset($x), ':', ($calls === 4), ';END;';
''',
    'peer-same-second-notequal-supplied-throw': b'''<?php
function peerSameSecondThrow103($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ':', $GLOBALS['calls'], ';';
    if ($GLOBALS['calls'] === 2) { throw $GLOBALS['chosen']; }
    return true;
}
$calls = 0; $chosen = new Exception('selected'); $result = 41;
set_error_handler('peerSameSecondThrow103');
try { $result = ($x != $x); echo 'BAD;'; }
catch (Exception $caught) { echo 'C:', ($caught === $chosen), ':', ($result === 41), ':', !isset($x), ':', ($calls === 2), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
}
