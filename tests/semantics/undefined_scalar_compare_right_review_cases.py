"""Independent missing-right scalar comparison originals, retained exactly."""

CASES = {
    'peer-plain-left-mutates-both-ops': b'''<?php
function peerPlainLeft92($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    $GLOBALS['missing'] = 9;
    $GLOBALS['left'] = 0;
    return true;
}
$left = 1;
set_error_handler('peerPlainLeft92');
$equal = ($left == $missing);
echo 'E:', ($equal === true), ':', ($missing === 9), ':', ($left === 0), ';';
unset($missing); $left = 1;
$less = ($left < $missing);
echo 'L:', ($less === false), ':', ($missing === 9), ':', ($left === 0), ';END;';
''',
    'peer-plain-left-becomes-reference-string': b'''<?php
function peerReferenceLeft92($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    $GLOBALS['missing'] = 9;
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = '0';
    return true;
}
$left = 0;
set_error_handler('peerReferenceLeft92');
$result = ($left
    ==
    $missing);
echo 'R:', ($result === false), ':', ($left === '0'), ':', ($alias === '0'), ':', ($missing === 9), ';';
$alias = 5;
echo 'A:', ($left === 5), ':', ($result === false), ';END;';
''',
    'peer-reference-left-rebinds-new-zero-cell': b'''<?php
function peerRebindLeft92($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    $GLOBALS['missing'] = 9;
    $GLOBALS['left'] =& $GLOBALS['target'];
    return true;
}
$left = '0';
$old =& $left;
$target = 0;
set_error_handler('peerRebindLeft92');
$result = ($left == $missing);
echo 'R:', ($result === true), ':', ($left === 0), ':', ($old === '0'), ':', ($missing === 9), ';';
$target = 5;
echo 'A:', ($left === 5), ':', ($old === '0'), ';END;';
''',
    'peer-left-unset-has-no-second-native-warning': b'''<?php
function peerUnsetLeft92($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    unset($GLOBALS['left']);
    $GLOBALS['missing'] = 9;
    return true;
}
$left = 1;
set_error_handler('peerUnsetLeft92');
$result = ($left == $missing);
echo 'R:', ($result === true), ':', !isset($left), ':', ($missing === 9), ';END;';
''',
}
