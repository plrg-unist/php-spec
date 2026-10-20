"""Original forward-comparison second-Warning sources frozen before implementation."""

CASES = {
    'peer-second-warning-equal-fresh-reference': b'''<?php
function peerSecondEqualReference100($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $left'), ':', ($m === 'Undefined variable $right'), ':', $line, ';';
    if ($m === 'Undefined variable $left') {
        $GLOBALS['left'] = 9;
    } else {
        $GLOBALS['alias'] =& $GLOBALS['right'];
        $GLOBALS['right'] = '0';
    }
    return true;
}
$result = 41;
set_error_handler('peerSecondEqualReference100');
$result = ($left
    ==
    $right);
echo 'R:', ($result === true), ':', ($left === 9), ':', ($right === '0'), ':', ($alias === '0'), ';';
$alias = 5;
echo 'A:', ($right === 5), ':', ($result === true), ';END;';
''',
    'peer-second-warning-less-unset-right-target-reference': b'''<?php
function peerSecondLessTarget100($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $left'), ':', ($m === 'Undefined variable $right'), ':', $line, ';';
    if ($m === 'Undefined variable $left') {
        unset($GLOBALS['right']);
    } else {
        $GLOBALS['right'] =& $GLOBALS['target'];
    }
    return false;
}
$right = 0; $target = '0'; $result = 41;
set_error_handler('peerSecondLessTarget100');
$result = ($left < $right);
echo 'R:', ($result === false), ':', !isset($left), ':', ($right === '0'), ';';
$target = 5;
echo 'A:', ($right === 5), ':', ($result === false), ';END;';
''',
    'peer-second-warning-notequal-less-equal-remain-missing': b'''<?php
function peerSecondMissing100($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $left'), ':', ($m === 'Undefined variable $right'), ':', $line, ';';
    return true;
}
$ne = 41; $le = 41;
set_error_handler('peerSecondMissing100');
$ne = ($left != $right);
$le = ($left <= $right);
echo 'R:', ($ne === false), ':', ($le === true), ':', !isset($left), ':', !isset($right), ';END;';
''',
    'peer-second-warning-notequal-supplied-throw': b'''<?php
function peerSecondNotEqualThrow100($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $left'), ':', ($m === 'Undefined variable $right'), ':', $line, ';';
    if ($m === 'Undefined variable $right') { throw $GLOBALS['chosen']; }
    return true;
}
$chosen = new Exception('selected'); $result = 41;
set_error_handler('peerSecondNotEqualThrow100');
try { $result = ($left != $right); echo 'BAD;'; }
catch (Exception $caught) { echo 'C:', ($caught === $chosen), ':', ($result === 41), ':', !isset($left), ':', !isset($right), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
}
