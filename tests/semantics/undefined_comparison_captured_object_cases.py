"""Captured ordinary objects, frozen missing NULL and saved-owner cleanup."""

CASES = {
    'captured-object-spaceship-left': b'''<?php
class SpaceCaptured114 {
    public function __destruct() {
        echo 'D:', $GLOBALS['result'] === 41, ';';
    }
}
$calls = 0;
$result = 41;
function warnSpaceCaptured114($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    unset($GLOBALS['saved']);
    $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('warnSpaceCaptured114');
$result = ($saved = new SpaceCaptured114()) <=> $missing;
echo 'R:', $result === 1, ':', $calls === 1, ':', !isset($saved), ':', $missing === 9, ';END;';
''',
    'captured-object-equal-right': b'''<?php
class EqualCaptured114 {
    public $tag = 1;
    public function __destruct() {
        echo 'D:', $GLOBALS['result'] === 41, ':', $this->tag === 7, ';';
    }
}
$source = new EqualCaptured114();
$alias =& $source;
$calls = 0;
$result = 41;
function warnEqualCaptured114($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['alias']->tag = 7;
    $GLOBALS['source'] = null;
    $GLOBALS['saved'] = null;
    unset($GLOBALS['alias']);
    $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('warnEqualCaptured114');
$result = $missing == ($saved = $source);
echo 'R:', $result === false, ':', $source === null, ':', $saved === null, ':', !isset($alias), ':', $missing === 9, ':', $calls === 1, ';END;';
''',
    'captured-object-constructor-no-init': b'''<?php
class MatrixCaptured114 {
    public function __destruct() { echo 'D;'; }
}
$calls = 0;
function warnMatrixCaptured114($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('warnMatrixCaptured114');
$a = (new MatrixCaptured114()) != $neMissing;
$b = (new MatrixCaptured114()) <= $leMissing;
$c = (new MatrixCaptured114()) > $gtMissing;
echo 'R:', $a === true, ':', $b === false, ':', $c === true, ':', $calls === 3, ':', !isset($neMissing), ':', !isset($leMissing), ':', !isset($gtMissing), ';END;';
''',
    'captured-object-greater-equal-default': b'''<?php
class DefaultCaptured114 {
    public $tag = 1;
    public function __destruct() {
        echo 'D:', $GLOBALS['result'] === 41, ':', $this->tag === 7, ';';
    }
}
$source = new DefaultCaptured114();
$calls = 0;
$result = 41;
function warnDefaultCaptured114($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['source']->tag = 7;
    unset($GLOBALS['source']);
    unset($GLOBALS['saved']);
    return false;
}
set_error_handler('warnDefaultCaptured114');
$result = $missing >= ($saved = $source);
echo 'R:', $result === false, ':', $calls === 1, ':', !isset($missing), ':', !isset($source), ':', !isset($saved), ';END;';
''',
    'captured-object-less-stdclass': b'''<?php
$source = new stdClass();
$source->tag = 1;
$calls = 0;
function warnStdCaptured114($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['source']->tag = 7;
    $GLOBALS['source'] = null;
    $GLOBALS['saved'] = null;
    $GLOBALS['missing'] = 9;
    return true;
}
set_error_handler('warnStdCaptured114');
$result = $missing < ($saved = $source);
echo 'R:', $result === true, ':', $source === null, ':', $saved === null, ':', $missing === 9, ':', $calls === 1, ';END;';
''',
    'captured-object-spaceship-throw': b'''<?php
class ThrowCaptured114 {
    public function __destruct() { echo 'D:', $GLOBALS['result'] === 41, ';'; }
}
$source = new ThrowCaptured114();
$chosen = new Exception('chosen114');
$calls = 0;
$result = 41;
function warnThrowCaptured114($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    unset($GLOBALS['source']);
    unset($GLOBALS['saved']);
    $GLOBALS['missing'] = 9;
    throw $GLOBALS['chosen'];
}
set_error_handler('warnThrowCaptured114');
try {
    $result = $missing <=> ($saved = $source);
    echo 'BAD;';
} catch (Exception $caught) {
    echo 'C:', $caught === $chosen, ':', $result === 41, ':', $calls === 1, ':', !isset($source), ':', !isset($saved), ':', $missing === 9, ';';
} finally {
    echo 'F;';
}
echo 'END;';
''',
    'captured-object-variable-boundary': b'''<?php
$source = new stdClass();
function warnVariableCaptured114($level, $message, $file, $line) { echo 'H|'; return true; }
set_error_handler('warnVariableCaptured114');
echo 'B|';
$result = $source == $missing;
echo $result ? '1' : '0';
''',
    'captured-object-closure-boundary': b'''<?php
function warnClosureCaptured114($level, $message, $file, $line) { echo 'H|'; return true; }
set_error_handler('warnClosureCaptured114');
echo 'B|';
$result = $missing <=> (function () {});
echo $result;
''',
}
