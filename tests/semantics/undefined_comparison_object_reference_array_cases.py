"""Object reference cells in comparison snapshots and current arrays."""
CASES = {
    'object-reference-array-captured-singleton': b'''<?php
class OldCapturedReference118 {
    public function __destruct() { echo 'O:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', ($GLOBALS['saved'] === [] && $GLOBALS['copy'] === []), ';'; }
}
class NewCapturedReference118 {
    public function __destruct() { echo 'N:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', $GLOBALS['saved'] === [], ';'; }
}
$calls = 0;
$result = 41;
$leaf = new OldCapturedReference118();
$saved = [&$leaf];
$copy = $saved;
unset($leaf);
function capturedObjectReference118() { return $GLOBALS['saved']; }
function warnCapturedObjectReference118($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['saved'][0] = new NewCapturedReference118();
    $GLOBALS['saved'] = [];
    $GLOBALS['copy'] = [];
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('warnCapturedObjectReference118');
$result = capturedObjectReference118() <=> $missing;
echo 'R:', $result === 1, ':', $saved === [], ':', $copy === [], ':', $missing === true, ':', $calls === 1, ';END;';
''',
    'object-reference-array-live-replacement': b'''<?php
class OldLiveReference118 {
    public function __destruct() { echo 'O:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', $GLOBALS['outside'] instanceof NewLiveReference118, ';'; }
}
class NewLiveReference118 {
    public function __destruct() { echo 'N:', $GLOBALS['result'] === true, ':', $GLOBALS['calls'] === 1, ':', !isset($GLOBALS['outside']), ';'; }
}
$calls = 0;
$result = 41;
$leaf = new OldLiveReference118();
$outside =& $leaf;
$right = [&$leaf];
$copy = $right;
function warnLiveObjectReference118($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['leaf'] = new NewLiveReference118();
    $GLOBALS['right'] = [];
    $GLOBALS['missing'] = 9;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('warnLiveObjectReference118');
$result = $missing == $right;
echo 'R:', $result === true, ':', $right === [], ':', $copy[0] === $outside, ':', $calls === 1, ';';
unset($copy, $leaf);
echo 'A:', (!isset($copy) && !isset($leaf)), ':', $outside instanceof NewLiveReference118, ';';
unset($outside);
echo 'END;';
''',
    'object-reference-array-created-shared-both': b'''<?php
$leaf = new stdClass();
$leaf->tag = 7;
$calls = 0;
function createdObjectReference118($level, $message, $file, $line) {
    global $calls, $leaf;
    $calls = $calls + 1;
    if ($calls === 1) { $GLOBALS['x'] = [&$leaf]; }
    else { $GLOBALS['right'] = [&$leaf]; }
    echo 'H:', $level === 2, ':', ($message === 'Undefined variable $x' || $message === 'Undefined variable $left'), ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('createdObjectReference118');
$a = $x > $x;
$b = $left <=> $right;
echo 'R:', $a === true, ':', $b === -1, ':', $calls === 2, ':', $x[0] === $leaf, ':', $right[0] === $leaf, ':', !isset($left), ';END;';
''',
    'object-reference-array-predicates-no-init': b'''<?php
$leaf = new stdClass();
$leaf->tag = 7;
$content = [&$leaf, 4];
$calls = 0;
function objectReferencePredicates118($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS['leaf']->tag = 8;
    if ($calls === 1) { $GLOBALS['savedA'] = []; }
    elseif ($calls === 2) { $GLOBALS['savedB'] = []; }
    elseif ($calls === 3) { $GLOBALS['savedC'] = []; }
    else { $GLOBALS['savedD'] = []; }
    echo 'H:', $level === 2, ':', ($message === 'Undefined variable $aMissing' || $message === 'Undefined variable $bMissing' || $message === 'Undefined variable $cMissing' || $message === 'Undefined variable $dMissing'), ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('objectReferencePredicates118');
$a = $aMissing != ($savedA = $content);
$b = $bMissing < ($savedB = $content);
$c = ($savedC = $content) <= $cMissing;
$d = $dMissing >= ($savedD = $content);
echo 'R:', $a === true, ':', $b === true, ':', $c === false, ':', $d === false, ':', $content[0]->tag === 8, ':', $leaf->tag === 8, ':', $savedA === [], ':', $savedB === [], ':', $savedC === [], ':', $savedD === [], ':', !isset($aMissing), ':', !isset($bMissing), ':', !isset($cMissing), ':', !isset($dMissing), ':', $calls === 4, ';END;';
''',
    'object-reference-array-live-greater-default': b'''<?php
$leaf = new stdClass();
$leaf->tag = 7;
$left = 0;
$calls = 0;
function defaultObjectReference118($level, $message, $file, $line) {
    global $calls, $leaf;
    $calls = $calls + 1;
    $GLOBALS['left'] = [&$leaf];
    $leaf->tag = 9;
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return false;
}
set_error_handler('defaultObjectReference118');
$result = $left > $missing;
echo 'R:', $result === true, ':', $left[0] === $leaf, ':', $leaf->tag === 9, ':', $missing === true, ':', $calls === 1, ';END;';
''',
    'object-reference-array-captured-greater-throw': b'''<?php
class ThrownObjectReference118 {
    public function __destruct() { echo 'D:', $GLOBALS['result'] === 41, ':', $GLOBALS['seen'] === 1, ';'; }
}
$leaf = new ThrownObjectReference118();
$content = [&$leaf];
unset($leaf);
$exception = new Exception('chosen118');
$result = 41;
$calls = 0;
$seen = 0;
function throwObjectReference118($level, $message, $file, $line) {
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
set_error_handler('throwObjectReference118');
try {
    $result = $missing > ($saved = $content);
    echo 'BAD;';
} catch (Exception $caught) {
    echo 'C:', $caught === $exception, ':', $result === 41, ':', !isset($content), ':', !isset($saved), ':', !isset($leaf), ':', $missing === true, ':', $calls === 1, ';';
} finally { echo 'F;'; }
echo 'END;';
''',
    'object-reference-array-internal-alias-entry-boundary': b'''<?php
$leaf = new Exception('internal');
$right = [&$leaf];
set_error_handler(function () { echo 'H|'; return true; });
echo 'B|';
$result = $missing <=> $right;
echo $result;
''',
    'object-reference-array-nested-alias-resume-boundary': b'''<?php
$leaf = new stdClass();
$right = [&$leaf];
set_error_handler(function () { echo 'H|'; $GLOBALS['leaf'] = [7]; return true; });
echo 'B|';
$result = $missing <=> $right;
echo $result;
''',
}
