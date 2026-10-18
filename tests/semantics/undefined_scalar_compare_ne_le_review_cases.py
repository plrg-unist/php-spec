"""Independent !=/<= warning originals retained byte-for-byte."""

CASES = {
    'peer-missing-left-reference-both-operators': b'''<?php
function peerRightReference93($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    $GLOBALS['missing'] = 9;
    $GLOBALS['alias'] =& $GLOBALS['right'];
    $GLOBALS['right'] = '0';
    return true;
}
$right = 0;
set_error_handler('peerRightReference93');
$notEqual = ($missing != $right);
echo 'N:', ($notEqual === true), ':', ($right === '0'), ':', ($missing === 9), ';';
unset($missing); $right = 0;
$lessEqual = ($missing <= $right);
echo 'P:', ($lessEqual === true), ':', ($right === '0'), ':', ($missing === 9), ';';
$alias = 5;
echo 'A:', ($right === 5), ';END;';
''',
    'peer-missing-right-late-left-reference-without-initializing-right': b'''<?php
function peerLeftReference93($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = '0';
    return true;
}
$left = 0;
set_error_handler('peerLeftReference93');
$result = ($left
    !=
    $missing);
echo 'R:', ($result === true), ':', ($left === '0'), ':', ($alias === '0'), ':', !isset($missing), ';';
$alias = 5;
echo 'A:', ($left === 5), ':', ($result === true), ';END;';
''',
    'peer-missing-right-left-reference-rebound-string': b'''<?php
function peerLeftRebind93($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    $GLOBALS['missing'] = 9;
    $GLOBALS['left'] =& $GLOBALS['target'];
    return true;
}
$left = 0;
$old =& $left;
$target = '0';
set_error_handler('peerLeftRebind93');
$result = ($left <= $missing);
echo 'R:', ($result === false), ':', ($left === '0'), ':', ($old === 0), ':', ($missing === 9), ';';
$target = 5;
echo 'A:', ($left === 5), ':', ($old === 0), ';END;';
''',
    'peer-missing-right-left-unset-has-one-warning': b'''<?php
function peerLeftUnset93($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    unset($GLOBALS['left']);
    $GLOBALS['missing'] = 9;
    return true;
}
$left = 1;
set_error_handler('peerLeftUnset93');
$result = ($left <= $missing);
echo 'R:', ($result === true), ':', !isset($left), ':', ($missing === 9), ';END;';
''',
}
