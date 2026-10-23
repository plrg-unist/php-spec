"""Reference-held flat child arrays at missing comparisons."""
CASES = {
    'array-payload-captured-singleton': b'''<?php
class OldCapturedChild119 {
    public function __destruct() { echo 'O:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', ($GLOBALS['saved'] === [] && $GLOBALS['copy'] === []), ';'; }
}
class NewCapturedChild119 {
    public function __destruct() { echo 'N:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', ($GLOBALS['saved'] === [] && $GLOBALS['copy'][0][1] === 4), ';'; }
}
$leaf = [new OldCapturedChild119(), 4];
$saved = [&$leaf];
$copy = $saved;
unset($leaf);
$result = 41;
$calls = 0;
function captureChildAlias119() { echo 'P;'; return $GLOBALS['saved']; }
function warnCapturedChildAlias119($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['saved'][0][1] = 9;
    $GLOBALS['saved'][0][0] = new NewCapturedChild119();
    echo 'I:', $GLOBALS['saved'][0][1] === 9, ':', $GLOBALS['copy'][0][1] === 4, ':', $GLOBALS['saved'][0][0] instanceof NewCapturedChild119, ':', $GLOBALS['copy'][0][0] instanceof OldCapturedChild119, ';';
    $GLOBALS['saved'] = [];
    $GLOBALS['copy'] = [];
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('warnCapturedChildAlias119');
$result = captureChildAlias119() <=> $missing;
echo 'R:', $result === 1, ':', $saved === [], ':', $copy === [], ':', $missing === true, ':', $calls === 1, ';END;';
''',
    'array-payload-live-replacement': b'''<?php
class OldLiveChild119 {
    public function __destruct() { echo 'O:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', ($GLOBALS['outside'][1] === 7 && $GLOBALS['held'] === []), ';'; }
}
class NewLiveChild119 {
    public function __destruct() { echo 'N:', $GLOBALS['result'] === true, ':', $GLOBALS['calls'] === 1, ':', !isset($GLOBALS['outside']), ';'; }
}
$leaf = [new OldLiveChild119(), 4];
$outside =& $leaf;
$right = [&$leaf];
$copy = $right;
$held = $leaf;
$result = 41;
$calls = 0;
function warnLiveChildAlias119($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['leaf'] = [new NewLiveChild119(), 7];
    echo 'I:', $GLOBALS['held'][1] === 4, ':', $GLOBALS['copy'][0][1] === 7, ':', $GLOBALS['outside'][0] instanceof NewLiveChild119, ':', $GLOBALS['copy'][0] === $GLOBALS['outside'], ';';
    $GLOBALS['held'] = [];
    $GLOBALS['right'] = [];
    $GLOBALS['missing'] = 9;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('warnLiveChildAlias119');
$result = $missing == $right;
echo 'R:', $result === true, ':', $right === [], ':', $copy[0][1] === 7, ':', $outside[0] instanceof NewLiveChild119, ':', $calls === 1, ':', $held === [], ':', $missing === 9, ';';
unset($copy, $leaf, $held);
echo 'A:', (!isset($copy) && !isset($leaf)), ':', $outside[1] === 7, ';';
unset($outside);
echo 'END;';
''',
    'array-payload-created-pooled-shared-both': b'''<?php
$leaf = [null, false, 7, 1.5, 'bytes'];
$calls = 0;
function createdObjectReference119($level, $message, $file, $line) {
    global $calls, $leaf;
    $calls = $calls + 1;
    if ($calls === 1) { $GLOBALS['x'] = [&$leaf]; }
    else { $GLOBALS['right'] = [&$leaf]; }
    echo 'H:', $level === 2, ':', ($message === 'Undefined variable $x' || $message === 'Undefined variable $left'), ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('createdObjectReference119');
$a = $x > $x;
$b = $left <=> $right;
echo 'R:', $a === true, ':', $b === -1, ':', $calls === 2, ':', $x[0] === $leaf, ':', $right[0] === $leaf, ':', !isset($left), ';END;';
''',
    'array-payload-empty-child-predicates-no-init': b'''<?php
$leaf = [];
$content = [&$leaf, 4];
$calls = 0;
function objectReferencePredicates119($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS['leaf'] = [8];
    if ($calls === 1) { $GLOBALS['savedA'] = []; }
    elseif ($calls === 2) { $GLOBALS['savedB'] = []; }
    elseif ($calls === 3) { $GLOBALS['savedC'] = []; }
    else { $GLOBALS['savedD'] = []; }
    echo 'H:', $level === 2, ':', ($message === 'Undefined variable $aMissing' || $message === 'Undefined variable $bMissing' || $message === 'Undefined variable $cMissing' || $message === 'Undefined variable $dMissing'), ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('objectReferencePredicates119');
$a = $aMissing != ($savedA = $content);
$b = $bMissing < ($savedB = $content);
$c = ($savedC = $content) <= $cMissing;
$d = $dMissing >= ($savedD = $content);
echo 'R:', $a === true, ':', $b === true, ':', $c === false, ':', $d === false, ':', $content[0][0] === 8, ':', $leaf[0] === 8, ':', $savedA === [], ':', $savedB === [], ':', $savedC === [], ':', $savedD === [], ':', !isset($aMissing), ':', !isset($bMissing), ':', !isset($cMissing), ':', !isset($dMissing), ':', $calls === 4, ';END;';
''',
    'array-payload-live-greater-default': b'''<?php
$leaf = [7];
$left = 0;
$calls = 0;
function defaultObjectReference119($level, $message, $file, $line) {
    global $calls, $leaf;
    $calls = $calls + 1;
    $GLOBALS['left'] = [&$leaf];
    $leaf[0] = 9;
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return false;
}
set_error_handler('defaultObjectReference119');
$result = $left > $missing;
echo 'R:', $result === true, ':', $left[0] === $leaf, ':', $leaf[0] === 9, ':', $missing === true, ':', $calls === 1, ';END;';
''',
    'array-payload-captured-greater-throw': b'''<?php
class ThrownObjectReference119 {
    public function __destruct() { echo 'D:', $GLOBALS['result'] === 41, ':', $GLOBALS['seen'] === 1, ';'; }
}
$leaf = [new ThrownObjectReference119()];
$content = [&$leaf];
unset($leaf);
$exception = new Exception('chosen119');
$result = 41;
$calls = 0;
$seen = 0;
function throwObjectReference119($level, $message, $file, $line) {
    global $calls, $exception;
    $calls = $calls + 1;
    $GLOBALS['content'] = [];
    $GLOBALS['saved'] = [];
    unset($GLOBALS['content'], $GLOBALS['saved']);
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['seen'] = 1;
    throw $exception;
}
set_error_handler('throwObjectReference119');
try {
    $result = $missing > ($saved = $content);
    echo 'BAD;';
} catch (Exception $caught) {
    echo 'C:', $caught === $exception, ':', $result === 41, ':', !isset($content), ':', !isset($saved), ':', !isset($leaf), ':', $missing === true, ':', $calls === 1, ';';
} finally { echo 'F;'; }
echo 'END;';
''',
    'array-payload-child-reference-ingress-boundary': b'''<?php
$inner = 4;
$leaf = [&$inner];
$right = [&$leaf];
set_error_handler(function () { echo 'H|'; return true; });
echo 'B|';
$result = $missing <=> $right;
echo $result;
''',
    'array-payload-deeper-child-resume-boundary': b'''<?php
$leaf = [7];
$right = [&$leaf];
set_error_handler(function () { echo 'H|'; $GLOBALS['leaf'] = [[8]]; return true; });
echo 'B|';
$result = $missing <=> $right;
echo $result;
''',
}
