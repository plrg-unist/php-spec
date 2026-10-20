"""Independent captured snapshots, unpooled roots, COW and abrupt release."""

CASES = {
    'peer-captured-left-returned-runtime': b'''<?php
$source = [];
$source[] = 4;
unset($source[0]);
$alias =& $source;
$calls = 0;
function captureLeft111() {
    global $source;
    echo 'P;';
    return $source;
}
function capturedLeftWarning111($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['alias'][] = 7;
    unset($GLOBALS['source']);
    $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('capturedLeftWarning111');
$result = (
    captureLeft111()
    <=> $missing
);
echo 'R:', $result === 0, ':', !isset($source), ':', $alias[1] === 7, ':', !isset($alias[0]), ':', $missing === 9, ':', $calls === 1, ';';
$alias[] = 8;
echo 'A:', $alias[2] === 8, ':', $alias[1] === 7, ':', $result === 0, ';END;';
''',
    'peer-captured-right-assignment-default': b'''<?php
$source = [];
$source[] = false;
$copy = $source;
$calls = 0;
function capturedRightWarning111($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['source'][0] = 7;
    $GLOBALS['saved'] = [];
    $GLOBALS['missing'] = 9;
    return false;
}
set_error_handler('capturedRightWarning111');
$result = (
    $missing
    <=> ($saved = $source)
);
echo 'R:', $result === -1, ':', $source[0] === 7, ':', $saved === [], ':', $copy[0] === false, ':', $missing === 9, ':', $calls === 1, ';';
$copy[0] = 8;
echo 'A:', $copy[0] === 8, ':', $source[0] === 7, ':', $saved === [], ':', $result === -1, ';END;';
''',
    'peer-captured-literal-no-initialization': b'''<?php
$calls = 0;
function capturedLiteralWarning111($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', ($message === 'Undefined variable $aMissing' || $message === 'Undefined variable $bMissing' || $message === 'Undefined variable $cMissing' || $message === 'Undefined variable $dMissing'), ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('capturedLiteralWarning111');
$a = [] <=> $aMissing;
$b = [false] <=> $bMissing;
$c = $cMissing <=> [false];
$d = $dMissing <=> [];
echo 'R:', $a === 0, ':', $b === 1, ':', $c === -1, ':', $d === 0, ':', !isset($aMissing), ':', !isset($bMissing), ':', !isset($cMissing), ':', !isset($dMissing), ':', $calls === 4, ';END;';
''',
    'peer-captured-runtime-supplied-throw': b'''<?php
$source = [];
$source[] = 4;
unset($source[0]);
$alias =& $source;
$exception = new Exception('chosen111');
$result = 41;
$calls = 0;
function captureThrow111() {
    global $source;
    echo 'P;';
    return $source;
}
function capturedThrowWarning111($level, $message, $file, $line) {
    global $calls, $exception;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['alias'][] = 7;
    unset($GLOBALS['source']);
    $GLOBALS['missing'] = 9;
    throw $exception;
}
set_error_handler('capturedThrowWarning111');
try {
    $result = captureThrow111() <=> $missing;
} catch (Exception $caught) {
    echo 'C:', $caught === $exception, ':', $result === 41, ':', !isset($source), ':', $alias[1] === 7, ':', !isset($alias[0]), ':', $missing === 9, ':', $calls === 1, ';';
} finally {
    echo 'F;';
}
$alias[] = 8;
echo 'A:', $alias[2] === 8, ':', $alias[1] === 7, ':', $result === 41, ';END;';
''',
}
