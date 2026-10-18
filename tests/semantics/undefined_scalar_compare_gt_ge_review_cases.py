"""Independent >/>= warning originals retained byte-for-byte."""

CASES = {
    'peer-missing-left-right-reference-both-operators': b'''<?php
function peerRightReference94($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    $GLOBALS['missing'] = 9;
    $GLOBALS['alias'] =& $GLOBALS['right'];
    $GLOBALS['right'] = '0';
    return true;
}
$right = 0;
set_error_handler('peerRightReference94');
$greaterEqual = ($missing
    >=
    $right);
echo 'G:', ($greaterEqual === false), ':', ($right === '0'), ':', ($missing === 9), ';';
unset($missing); $right = 0;
$greater = ($missing > $right);
echo 'P:', ($greater === false), ':', ($right === '0'), ':', ($missing === 9), ';';
$alias = 5;
echo 'A:', ($right === 5), ';END;';
''',
    'peer-missing-right-left-reference-rebound-string': b'''<?php
function peerLeftRebind94($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    $GLOBALS['missing'] = 9;
    $GLOBALS['left'] =& $GLOBALS['target'];
    return true;
}
$left = 0;
$old =& $left;
$target = '0';
set_error_handler('peerLeftRebind94');
$result = ($left > $missing);
echo 'R:', ($result === true), ':', ($left === '0'), ':', ($old === 0), ':', ($missing === 9), ';';
$target = 5;
echo 'A:', ($left === 5), ':', ($old === 0), ';END;';
''',
    'peer-missing-right-late-left-reference-without-initializing-right': b'''<?php
function peerLeftReference94($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = '0';
    return true;
}
$left = 0;
set_error_handler('peerLeftReference94');
$result = ($left
    >=
    $missing);
echo 'R:', ($result === true), ':', ($left === '0'), ':', ($alias === '0'), ':', !isset($missing), ';';
$alias = 5;
echo 'A:', ($left === 5), ':', ($result === true), ';END;';
''',
    'peer-missing-left-right-unset-has-one-warning': b'''<?php
function peerRightUnset94($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    unset($GLOBALS['right']);
    $GLOBALS['missing'] = 9;
    return true;
}
$right = 1;
set_error_handler('peerRightUnset94');
$result = ($missing >= $right);
echo 'R:', ($result === true), ':', !isset($right), ':', ($missing === 9), ';END;';
''',
}
