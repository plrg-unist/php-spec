"""Independent live-left CV wrappers, rebinding and unreadable boundaries."""

CASES = {
    'peer-plain-left-becomes-reference-string': b'''<?php
function peerPlainLeft90($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    $GLOBALS['missing'] = 9;
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = '0';
    return true;
}
$left = 0;
set_error_handler('peerPlainLeft90');
$result = ($left
    <=>
    $missing);
echo 'R:', ($result === 1), ':', ($left === '0'), ':', ($alias === '0'), ':', ($missing === 9), ';';
$alias = 5;
echo 'A:', ($left === 5), ':', ($result === 1), ';END;';
''',
    'peer-reference-left-rebinds-new-cell': b'''<?php
function peerRebindLeft90($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    $GLOBALS['missing'] = 9;
    $GLOBALS['left'] =& $GLOBALS['target'];
    return true;
}
$left = 2;
$old =& $left;
$target = 0;
set_error_handler('peerRebindLeft90');
$result = ($left <=> $missing);
echo 'R:', ($result === 0), ':', ($left === 0), ':', ($old === 2), ':', ($missing === 9), ';';
$target = 'after';
echo 'A:', ($left === 'after'), ':', ($old === 2), ';END;';
''',
    'peer-left-unset-has-no-second-native-warning': b'''<?php
function peerUnsetLeft90($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    unset($GLOBALS['left']);
    $GLOBALS['missing'] = 9;
    return true;
}
$left = 2;
set_error_handler('peerUnsetLeft90');
$result = ($left <=> $missing);
echo 'R:', ($result === 0), ':', !isset($left), ':', ($missing === 9), ';END;';
''',
}
