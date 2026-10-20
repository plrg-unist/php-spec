"""Physical right-first comparisons across two missing-CV Warnings."""

CASES = {
    'peer-second-warning-greater-fresh-reference': b'''<?php
function peerSecondGreaterReference101($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $right'), ':', ($m === 'Undefined variable $left'), ':', $line, ';';
    if ($m === 'Undefined variable $right') {
        $GLOBALS['right'] = 9;
    } else {
        $GLOBALS['alias'] =& $GLOBALS['left'];
        $GLOBALS['left'] = '0';
    }
    return true;
}
$result = 41;
set_error_handler('peerSecondGreaterReference101');
$result = ($left
    >
    $right);
echo 'R:', ($result === false), ':', ($right === 9), ':', ($left === '0'), ':', ($alias === '0'), ';';
$alias = 5;
echo 'A:', ($left === 5), ':', ($result === false), ';END;';
''',
    'peer-second-warning-greaterequal-unset-left-target-reference': b'''<?php
function peerSecondGreaterEqualTarget101($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $right'), ':', ($m === 'Undefined variable $left'), ':', $line, ';';
    if ($m === 'Undefined variable $right') {
        unset($GLOBALS['left']);
    } else {
        $GLOBALS['left'] =& $GLOBALS['target'];
    }
    return false;
}
$left = 0; $target = '0'; $result = 41;
set_error_handler('peerSecondGreaterEqualTarget101');
$result = ($left >= $right);
echo 'R:', ($result === true), ':', !isset($right), ':', ($left === '0'), ';';
$target = 5;
echo 'A:', ($left === 5), ':', ($result === true), ';END;';
''',
    'peer-second-warning-greater-greaterequal-remain-missing': b'''<?php
function peerSecondReversedMissing101($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $right'), ':', ($m === 'Undefined variable $left'), ':', $line, ';';
    return true;
}
$gt = 41; $ge = 41;
set_error_handler('peerSecondReversedMissing101');
$gt = ($left > $right);
$ge = ($left >= $right);
echo 'R:', ($gt === false), ':', ($ge === true), ':', !isset($left), ':', !isset($right), ';END;';
''',
    'peer-second-warning-greaterequal-supplied-throw': b'''<?php
function peerSecondGreaterEqualThrow101($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $right'), ':', ($m === 'Undefined variable $left'), ':', $line, ';';
    if ($m === 'Undefined variable $left') { throw $GLOBALS['chosen']; }
    return true;
}
$chosen = new Exception('selected'); $result = 41;
set_error_handler('peerSecondGreaterEqualThrow101');
try { $result = ($left >= $right); echo 'BAD;'; }
catch (Exception $caught) { echo 'C:', ($caught === $chosen), ':', ($result === 41), ':', !isset($left), ':', !isset($right), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
}
