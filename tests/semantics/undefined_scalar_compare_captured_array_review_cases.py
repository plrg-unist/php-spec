"""Independent captured Boolean snapshots and abrupt saved-owner release."""

CASES = {
    'peer-captured-equal-returned-empty': b'''<?php
$source = [];
$source[] = 4;
unset($source[0]);
$alias =& $source;
$calls = 0;
function capturedEqual112() {
    global $source;
    echo 'P;';
    return $source;
}
function equalSnapshotWarning112($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['alias'][] = 7;
    unset($GLOBALS['source']);
    $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('equalSnapshotWarning112');
$result = (
    capturedEqual112()
    == $missing
);
echo 'R:', $result === true, ':', !isset($source), ':', $alias[1] === 7, ':', !isset($alias[0]), ':', $missing === 9, ':', $calls === 1, ';';
$alias[] = 8;
echo 'A:', $alias[2] === 8, ':', $alias[1] === 7, ':', $result === true, ';END;';
''',
    'peer-captured-greater-equal-right-default': b'''<?php
$source = [];
$source[] = 4;
unset($source[0]);
$copy = $source;
$calls = 0;
function greaterEqualSnapshot112($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['source'][] = 7;
    $GLOBALS['saved'] = [false];
    $GLOBALS['missing'] = 9;
    return false;
}
set_error_handler('greaterEqualSnapshot112');
$result = (
    $missing
    >= ($saved = $source)
);
echo 'R:', $result === true, ':', $source[1] === 7, ':', $saved[0] === false, ':', $copy === [], ':', $missing === 9, ':', $calls === 1, ';';
$copy[] = 8;
echo 'A:', $copy[1] === 8, ':', $source[1] === 7, ':', $saved[0] === false, ':', $result === true, ';END;';
''',
    'peer-captured-predicate-snapshots-no-init': b'''<?php
$empty = [];
$nonempty = [false];
$calls = 0;
function predicateSnapshots112($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', ($message === 'Undefined variable $aMissing' || $message === 'Undefined variable $bMissing' || $message === 'Undefined variable $cMissing' || $message === 'Undefined variable $dMissing'), ':', $line, ':', $calls, ';';
    if ($calls === 1) { $GLOBALS['savedA'] = [false]; }
    elseif ($calls === 2) { $GLOBALS['savedB'] = [false]; }
    elseif ($calls === 3) { $GLOBALS['savedC'] = []; }
    else { $GLOBALS['savedD'] = []; }
    return true;
}
set_error_handler('predicateSnapshots112');
$a = $aMissing != ($savedA = $empty);
$b = $bMissing < ($savedB = $empty);
$c = ($savedC = $nonempty) <= $cMissing;
$d = ($savedD = $nonempty) > $dMissing;
echo 'R:', $a === false, ':', $b === false, ':', $c === false, ':', $d === true, ':', !isset($aMissing), ':', !isset($bMissing), ':', !isset($cMissing), ':', !isset($dMissing), ':', $calls === 4, ';END;';
''',
    'peer-captured-less-supplied-throw': b'''<?php
$source = [];
$source[] = 4;
unset($source[0]);
$alias =& $source;
$exception = new Exception('chosen112');
$result = 41;
$calls = 0;
function capturedLess112() {
    global $source;
    echo 'P;';
    return $source;
}
function lessSnapshotThrow112($level, $message, $file, $line) {
    global $calls, $exception;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['alias'][] = 7;
    unset($GLOBALS['source']);
    $GLOBALS['missing'] = 9;
    throw $exception;
}
set_error_handler('lessSnapshotThrow112');
try {
    $result = capturedLess112() < $missing;
} catch (Exception $caught) {
    echo 'C:', $caught === $exception, ':', $result === 41, ':', !isset($source), ':', $alias[1] === 7, ':', !isset($alias[0]), ':', $missing === 9, ':', $calls === 1, ';';
} finally {
    echo 'F;';
}
$alias[] = 8;
echo 'A:', $alias[2] === 8, ':', $alias[1] === 7, ':', $result === 41, ';END;';
''',
}
