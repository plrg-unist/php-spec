"""Independent object-array snapshots, COW and last-child release."""

CASES = {
    'peer-object-array-captured-spaceship-cow': b'''<?php
class SavedArrayLeaf116 {
    public $tag = 7;
    function __destruct() {
        echo 'D:', $GLOBALS['result'] === 41, ':', $this->tag === 7, ';';
    }
}
$source = [new SavedArrayLeaf116];
$result = 41;
$calls = 0;
function capturedArray116() {
    global $source;
    echo 'P;';
    return $source;
}
function capturedArrayWarning116($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['source'][0] = 8;
    $GLOBALS['source'] = [];
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('capturedArrayWarning116');
$result = (
    capturedArray116()
    <=> $missing
);
echo 'R:', $result === 1, ':', $source === [], ':', $missing === true, ':', $calls === 1, ';';
$source[] = 9;
echo 'A:', $source[0] === 9, ':', $result === 1, ';END;';
''',
    'peer-object-array-equal-target-default': b'''<?php
class OldArrayLeaf116 {
    public $tag = 4;
    function __destruct() { echo 'O:', $GLOBALS['result'] === false, ';'; }
}
class NewArrayLeaf116 {
    public $tag = 7;
    function __destruct() { echo 'N:', $GLOBALS['result'] === false, ';'; }
}
$target = [new OldArrayLeaf116];
$copy = $target;
$source = 0;
$result = 41;
$calls = 0;
function currentArrayWarning116($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS['source'] =& $GLOBALS['target'];
    $GLOBALS['target'][0] = new NewArrayLeaf116;
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return false;
}
set_error_handler('currentArrayWarning116');
$result = (
    $missing
    == $source
);
echo 'R:', $result === false, ':', $source[0]->tag === 7, ':', $target[0]->tag === 7, ':', $copy[0]->tag === 4, ':', $missing === true, ':', $calls === 1, ';';
$source[1] = 8;
echo 'A:', $target[1] === 8, ':', !isset($copy[1]), ':', $copy[0]->tag === 4, ';';
unset($source, $target);
unset($copy);
echo 'END;';
''',
    'peer-object-array-predicates-no-init': b'''<?php
class QuietArrayLeaf116 { public $tag = 7; }
$content = [new QuietArrayLeaf116];
$calls = 0;
function predicateArrayWarning116($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS['content'][0]->tag = 8;
    if ($calls === 1) { $GLOBALS['savedA'] = []; }
    elseif ($calls === 2) { $GLOBALS['savedB'] = []; }
    elseif ($calls === 3) { $GLOBALS['savedC'] = []; }
    else { $GLOBALS['savedD'] = []; }
    echo 'H:', $level === 2, ':', ($message === 'Undefined variable $aMissing' || $message === 'Undefined variable $bMissing' || $message === 'Undefined variable $cMissing' || $message === 'Undefined variable $dMissing'), ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('predicateArrayWarning116');
$a = $aMissing != ($savedA = $content);
$b = $bMissing < ($savedB = $content);
$c = ($savedC = $content) <= $cMissing;
$d = $dMissing >= ($savedD = $content);
echo 'R:', $a === true, ':', $b === true, ':', $c === false, ':', $d === false, ':', $content[0]->tag === 8, ':', $savedA === [], ':', $savedB === [], ':', $savedC === [], ':', $savedD === [], ':', !isset($aMissing), ':', !isset($bMissing), ':', !isset($cMissing), ':', !isset($dMissing), ':', $calls === 4, ';END;';
''',
    'peer-object-array-captured-supplied-throw': b'''<?php
class ThrownArrayLeaf116 {
    public $tag = 7;
    function __destruct() {
        echo 'D:', $GLOBALS['result'] === 41, ':', $GLOBALS['seen'] === 1, ':', $this->tag === 8, ';';
    }
}
$source = [new ThrownArrayLeaf116];
$alias =& $source;
$exception = new Exception('chosen116');
$result = 41;
$seen = 0;
$calls = 0;
function capturedThrowArray116() {
    global $source;
    echo 'P;';
    return $source;
}
function throwArrayWarning116($level, $message, $file, $line) {
    global $calls, $exception;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['alias'][0]->tag = 8;
    $GLOBALS['alias'] = [];
    unset($GLOBALS['source'], $GLOBALS['alias']);
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['seen'] = 1;
    throw $exception;
}
set_error_handler('throwArrayWarning116');
try {
    $result = capturedThrowArray116() <= $missing;
} catch (Exception $caught) {
    echo 'C:', $caught === $exception, ':', $result === 41, ':', !isset($source), ':', !isset($alias), ':', $missing === true, ':', $calls === 1, ';';
} finally {
    echo 'F;';
}
echo 'END;';
''',
}
