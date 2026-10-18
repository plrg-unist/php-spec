"""Independent frozen-null, live scalar, captured-value and abrupt comparisons."""

CASES = {
    'peer-null-string-reference-rebind': b'''<?php
function scalarPeerRebind89($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    $GLOBALS['missing'] = 9;
    $GLOBALS['right'] =& $GLOBALS['target'];
    return true;
}
$right = 2;
$old =& $right;
$target = '0';
set_error_handler('scalarPeerRebind89');
$result = ($missing
    <=>
    $right);
echo 'R:', ($result === -1), ':', ($missing === 9), ':', ($right === '0'), ':', ($old === 2), ';';
$target = 'after';
echo 'A:', ($right === 'after'), ':', ($old === 2), ';END;';
''',
    'peer-captured-right-expression': b'''<?php
function scalarPeerCaptured89($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', ($GLOBALS['right'] === 1), ':', $line, ';';
    $GLOBALS['missing'] = 9;
    $GLOBALS['right'] = 0;
    return true;
}
$right = 2;
set_error_handler('scalarPeerCaptured89');
$result = ($missing <=> ($right = 1));
echo 'R:', ($result === -1), ':', ($right === 0), ':', ($missing === 9), ';END;';
''',
    'peer-false-default-then-live-null': b'''<?php
function scalarPeerFalse89($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    $GLOBALS['missing'] = 9;
    $GLOBALS['right'] = null;
    return false;
}
$right = '0';
set_error_handler('scalarPeerFalse89');
$result = ($missing <=> $right);
echo 'R:', ($result === 0), ':', ($right === null), ':', ($missing === 9), ';END;';
''',
    'peer-handler-throw-preserves-destination': b'''<?php
function scalarPeerThrow89($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    $GLOBALS['missing'] = 9;
    $GLOBALS['right'] = false;
    throw $GLOBALS['chosen'];
}
$right = '0';
$result = 41;
$chosen = new Exception('selected');
set_error_handler('scalarPeerThrow89');
try {
    $result = ($missing <=> $right);
    echo 'BAD;';
} catch (Exception $caught) {
    echo 'C:', ($caught === $chosen), ':', ($result === 41), ':', ($missing === 9), ':', ($right === false), ';';
} finally {
    echo 'F;';
}
echo 'END;';
''',
}
