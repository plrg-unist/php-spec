"""Independent primitive-reference arrays, container COW and saved release."""

CASES = {
    'peer-reference-array-captured-spaceship-cow': b'''<?php
$leaf = 0;
$outside =& $leaf;
$source = [&$leaf];
$copy = $source;
$result = 41;
$calls = 0;
function capturedSharedReference117() {
    global $source;
    echo 'P;';
    return $source;
}
function capturedSharedWarning117($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['source'][1] = 8;
    $GLOBALS['leaf'] = 7;
    echo 'I:', $GLOBALS['source'][0] === 7, ':', $GLOBALS['copy'][0] === 7, ':', !isset($GLOBALS['copy'][1]), ';';
    $GLOBALS['source'] = [];
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('capturedSharedWarning117');
$result = (
    capturedSharedReference117()
    <=> $missing
);
echo 'R:', $result === 1, ':', $source === [], ':', $copy[0] === 7, ':', $leaf === 7, ':', $outside === 7, ':', $calls === 1, ':', $missing === true, ';';
$copy[0] = 9;
echo 'A:', $leaf === 9, ':', $outside === 9, ';';
unset($copy);
$outside = 11;
echo 'L:', $leaf === 11, ':', !isset($copy), ';END;';
''',
    'peer-reference-array-equal-target-default': b'''<?php
$leaf = 0;
$target = [&$leaf];
$copy = $target;
$source = 0;
$result = 41;
$calls = 0;
function currentSharedWarning117($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS['source'] =& $GLOBALS['target'];
    $GLOBALS['target'][1] = 8;
    $GLOBALS['leaf'] = 7;
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return false;
}
set_error_handler('currentSharedWarning117');
$result = (
    $missing
    == $source
);
echo 'R:', $result === false, ':', $source[0] === 7, ':', $target[1] === 8, ':', $copy[0] === 7, ':', !isset($copy[1]), ':', $calls === 1, ':', $missing === true, ';';
$source[2] = 9;
echo 'A:', $target[2] === 9, ':', !isset($copy[2]), ';';
$copy[0] = 11;
echo 'W:', $leaf === 11, ':', $source[0] === 11, ':', $target[0] === 11, ';';
unset($source, $target, $copy);
$leaf = 12;
echo 'Z:', $leaf === 12, ';END;';
''',
    'peer-reference-array-predicates-no-init': b'''<?php
$leaf = 0;
$content = [&$leaf];
$calls = 0;
function predicateSharedWarning117($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS['leaf'] = 7;
    if ($calls === 1) { $GLOBALS['savedA'] = []; }
    elseif ($calls === 2) { $GLOBALS['savedB'] = []; }
    elseif ($calls === 3) { $GLOBALS['savedC'] = []; }
    else { $GLOBALS['savedD'] = []; }
    echo 'H:', $level === 2, ':', ($message === 'Undefined variable $aMissing' || $message === 'Undefined variable $bMissing' || $message === 'Undefined variable $cMissing' || $message === 'Undefined variable $dMissing'), ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('predicateSharedWarning117');
$a = $aMissing != ($savedA = $content);
$b = $bMissing < ($savedB = $content);
$c = ($savedC = $content) <= $cMissing;
$d = $dMissing >= ($savedD = $content);
echo 'R:', $a === true, ':', $b === true, ':', $c === false, ':', $d === false, ':', $content[0] === 7, ':', $leaf === 7, ':', $savedA === [], ':', $savedB === [], ':', $savedC === [], ':', $savedD === [], ':', !isset($aMissing), ':', !isset($bMissing), ':', !isset($cMissing), ':', !isset($dMissing), ':', $calls === 4, ';';
$content[0] = 8;
echo 'A:', $leaf === 8, ';END;';
''',
    'peer-reference-array-captured-supplied-throw': b'''<?php
$leaf = 0;
$outside =& $leaf;
$source = [&$leaf];
$exception = new Exception('chosen117');
$result = 41;
$seen = 0;
$calls = 0;
function capturedThrowReference117() {
    global $source;
    echo 'P;';
    return $source;
}
function throwSharedWarning117($level, $message, $file, $line) {
    global $calls, $exception;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['leaf'] = 7;
    $GLOBALS['source'] = [];
    unset($GLOBALS['source']);
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['seen'] = 1;
    throw $exception;
}
set_error_handler('throwSharedWarning117');
try {
    $result = capturedThrowReference117() <=> $missing;
    echo 'BAD;';
} catch (Exception $caught) {
    echo 'C:', $caught === $exception, ':', $result === 41, ':', $outside === 7, ':', $leaf === 7, ':', !isset($source), ':', $missing === true, ':', $seen === 1, ':', $calls === 1, ';';
} finally { echo 'F;'; }
$outside = 11;
echo 'Z:', $leaf === 11, ';END;';
''',
}
