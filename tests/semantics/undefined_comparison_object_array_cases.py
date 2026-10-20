"""Flat DIRECT object leaves, current/COW tables and transitive release."""

CASES = {
    'object-array-captured-spaceship-left': b'''<?php
class CapturedLeaf116 {
    public function __destruct() { echo 'D:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ';'; }
}
$leaf = new CapturedLeaf116();
$saved = [$leaf];
unset($leaf);
$calls = 0;
$result = 41;
function capturedArray116() { return $GLOBALS['saved']; }
function warnCapturedArray116($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['saved'] = [];
    $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('warnCapturedArray116');
$result = capturedArray116() <=> $missing;
echo 'R:', $result === 1, ':', $saved === [], ':', $missing === 9, ':', $calls === 1, ';END;';
''',
    'object-array-live-equal-right': b'''<?php
class CurrentLeaf116 {
    public function __destruct() { echo 'D:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ';'; }
}
$right = [new CurrentLeaf116()];
$calls = 0;
$result = 41;
function warnCurrentArray116($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['right'] = [];
    $GLOBALS['missing'] = 9;
    echo 'A;';
    return true;
}
set_error_handler('warnCurrentArray116');
$result = $missing == $right;
echo 'R:', $result === true, ':', $right === [], ':', $missing === 9, ':', $calls === 1, ';END;';
''',
    'object-array-greater-created-stdclass': b'''<?php
$left = 0;
$calls = 0;
function warnCreatedArray116($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS['left'] = [0, new stdClass()];
    $GLOBALS['missing'] = [];
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('warnCreatedArray116');
$result = $left > $missing;
echo 'R:', $result === true, ':', $left[1] instanceof stdClass, ':', $missing === [], ':', $calls === 1, ';END;';
''',
    'object-array-predicates-no-init': b'''<?php
class PredicateLeaf116 { public $tag = 7; }
$content = [1, new PredicateLeaf116()];
$calls = 0;
function warnPredicateArray116($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS['held'] = [];
    $GLOBALS['content'][1]->tag = 8;
    echo 'H:', $level === 2, ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('warnPredicateArray116');
$a = $aMissing != ($held = $content);
$b = $bMissing < $content;
$c = ($held = $content) <= $cMissing;
$d = $dMissing >= ($held = $content);
echo 'R:', $a === true, ':', $b === true, ':', $c === false, ':', $d === false, ':', $content[1]->tag === 8, ':', $held === [], ':', !isset($aMissing), ':', !isset($bMissing), ':', !isset($cMissing), ':', !isset($dMissing), ':', $calls === 4, ';END;';
''',
    'object-array-live-spaceship-default': b'''<?php
class DefaultLeaf116 {
    public function __destruct() { echo 'D:', $GLOBALS['result'] === 41, ';'; }
}
$left = [new DefaultLeaf116()];
$calls = 0;
$result = 41;
function warnDefaultArray116($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS['left'] = [];
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return false;
}
set_error_handler('warnDefaultArray116');
$result = $left <=> $missing;
echo 'R:', $result === 0, ':', $left === [], ':', $missing === true, ':', $calls === 1, ';END;';
''',
    'object-array-captured-greater-throw': b'''<?php
class ThrowLeaf116 {
    public function __destruct() { echo 'D:', $GLOBALS['result'] === 41, ':', $GLOBALS['seen'] === 1, ';'; }
}
$chosen = new Exception('chosen116');
$calls = 0;
$seen = 0;
$result = 41;
function warnThrowArray116($level, $message, $file, $line) {
    global $calls, $chosen;
    $calls = $calls + 1;
    $GLOBALS['saved'] = [];
    $GLOBALS['missing'] = 9;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['seen'] = 1;
    throw $chosen;
}
set_error_handler('warnThrowArray116');
try {
    $result = $missing > ($saved = [new ThrowLeaf116()]);
} catch (Exception $caught) {
    echo 'C:', $caught === $chosen, ':', $result === 41, ':', $saved === [], ':', $missing === 9, ':', $calls === 1, ';';
} finally { echo 'F;'; }
echo 'END;';
''',
    'object-array-alias-entry-boundary': b'''<?php
$value = 7;
$right = [&$value];
function warnAliasArray116($level, $message, $file, $line) { echo 'H|'; return true; }
set_error_handler('warnAliasArray116');
echo 'B|';
$result = $missing == $right;
echo $result ? '1' : '0';
''',
    'object-array-nested-resume-boundary': b'''<?php
class NestedLeaf116 {}
$right = 0;
function warnNestedArray116($level, $message, $file, $line) {
    echo 'H|';
    $GLOBALS['right'] = [[new NestedLeaf116()]];
    return true;
}
set_error_handler('warnNestedArray116');
echo 'B|';
$result = $missing <=> $right;
echo $result;
''',
}
