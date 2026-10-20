"""Original primitive-reference arrays against frozen missing NULL."""
CASES = {
    'reference-array-captured-singleton': b'''<?php
$leaf = 7;
$saved = [&$leaf];
$copy = $saved;
unset($leaf);
$calls = 0;
$result = 41;
function capturedReference117() { return $GLOBALS['saved']; }
function warnCapturedReference117($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['saved'][0] = 9;
    echo 'A:', $GLOBALS['copy'][0] === 7, ':', $GLOBALS['saved'][0] === 9, ';';
    $GLOBALS['saved'] = [];
    $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('warnCapturedReference117');
$result = capturedReference117() <=> $missing;
echo 'R:', $result === 1, ':', $copy[0] === 7, ':', $saved === [], ':', $missing === 9, ':', $calls === 1, ';';
unset($copy);
echo 'L:', !isset($copy), ';END;';
''',
    'reference-array-live-equal': b'''<?php
$leaf = 7;
$right = [&$leaf, &$leaf];
$copy = $right;
$calls = 0;
$result = 41;
function warnLiveReference117($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['right'] = [];
    $GLOBALS['leaf'] = 9;
    $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('warnLiveReference117');
$result = $missing == $right;
echo 'R:', $result === true, ':', $right === [], ':', $leaf === 9, ':', $copy[0] === 9, ':', $copy[1] === 9, ':', $calls === 1, ';';
$copy[0] = 11;
echo 'A:', $leaf === 11, ':', $copy[1] === 11, ';';
unset($copy);
$leaf = 12;
echo 'Z:', $leaf === 12, ':', $right === [], ';END;';
''',
    'reference-array-created-greater-both': b'''<?php
$leaf = 0;
$calls = 0;
function createdReference117($level, $message, $file, $line) {
    global $calls, $leaf;
    $calls = $calls + 1;
    if ($calls === 1) { $GLOBALS['x'] = [&$leaf, new stdClass()]; }
    else { $GLOBALS['right'] = [&$leaf]; }
    echo 'H:', $level === 2, ':', ($message === 'Undefined variable $x' || $message === 'Undefined variable $left'), ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('createdReference117');
$a = $x > $x;
$b = $left <=> $right;
echo 'R:', $a === true, ':', $b === -1, ':', $calls === 2, ':', $x[0] === 0, ':', $right[0] === 0, ':', !isset($left), ';END;';
''',
    'reference-array-predicates-no-init': b'''<?php
$i = 1;
$f = 1.5;
$s = '0';
$b = false;
$n = null;
$content = [&$i, &$f, &$s, &$b, &$n];
$calls = 0;
function primitiveReferences117($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS['i'] = 7;
    $GLOBALS['f'] = 2.5;
    $GLOBALS['s'] = 'changed';
    $GLOBALS['b'] = true;
    if ($calls === 1) { $GLOBALS['savedA'] = []; }
    elseif ($calls === 2) { $GLOBALS['savedB'] = []; }
    elseif ($calls === 3) { $GLOBALS['savedC'] = []; }
    else { $GLOBALS['savedD'] = []; }
    echo 'H:', $level === 2, ':', ($message === 'Undefined variable $aMissing' || $message === 'Undefined variable $bMissing' || $message === 'Undefined variable $cMissing' || $message === 'Undefined variable $dMissing'), ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('primitiveReferences117');
$a = $aMissing != ($savedA = $content);
$less = $bMissing < ($savedB = $content);
$le = ($savedC = $content) <= $cMissing;
$ge = $dMissing >= ($savedD = $content);
echo 'R:', $a === true, ':', $less === true, ':', $le === false, ':', $ge === false, ':', $content[0] === 7, ':', $content[1] === 2.5, ':', $content[2] === 'changed', ':', $content[3] === true, ':', $content[4] === null, ':', $calls === 4, ':', !isset($aMissing), ':', !isset($bMissing), ':', !isset($cMissing), ':', !isset($dMissing), ';END;';
''',
    'reference-array-live-ge-default': b'''<?php
$leaf = 7;
$left = [&$leaf];
$calls = 0;
function defaultReference117($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS['left'] = [];
    $GLOBALS['leaf'] = 9;
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return false;
}
set_error_handler('defaultReference117');
$result = $left >= $missing;
echo 'R:', $result === true, ':', $left === [], ':', $leaf === 9, ':', $missing === true, ':', $calls === 1, ';END;';
''',
    'reference-array-captured-greater-throw': b'''<?php
$leaf = 0;
$outside =& $leaf;
$content = [&$leaf];
$exception = new Exception('chosen117');
$result = 41;
$calls = 0;
function thrownReference117($level, $message, $file, $line) {
    global $calls, $exception;
    $calls = $calls + 1;
    $GLOBALS['leaf'] = 7;
    $GLOBALS['saved'] = [];
    unset($GLOBALS['saved']);
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    throw $exception;
}
set_error_handler('thrownReference117');
try {
    $result = $missing > ($saved = $content);
    echo 'BAD;';
} catch (Exception $caught) {
    echo 'C:', $caught === $exception, ':', $result === 41, ':', $outside === 7, ':', $content[0] === 7, ':', !isset($saved), ':', $calls === 1, ';';
} finally { echo 'F;'; }
$outside = 9;
echo 'A:', $content[0] === 9, ':', $leaf === 9, ';END;';
''',
    'reference-array-object-alias-entry-boundary': b'''<?php
$leaf = new stdClass();
$right = [&$leaf];
set_error_handler(function () { echo 'H|'; return true; });
echo 'B|';
$result = $missing <=> $right;
echo $result;
''',
    'reference-array-nested-alias-resume-boundary': b'''<?php
$leaf = 0;
$right = [&$leaf];
set_error_handler(function () { echo 'H|'; $GLOBALS['leaf'] = [7]; return true; });
echo 'B|';
$result = $missing <=> $right;
echo $result;
''',
}
