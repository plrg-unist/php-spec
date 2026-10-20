"""Independent shared object cells, COW and last-chain retirement."""

CASES = {
    'peer-object-reference-array-captured-shared-cow': b'''<?php
class SharedOld118 {
    public $tag = 4;
    function __destruct() { echo 'O:', $GLOBALS['result'] === 41, ';'; }
}
class SharedNew118 {
    public $tag = 7;
    function __destruct() {
        echo 'N:', $GLOBALS['result'] === 41, ':', $this->tag === 9, ':', $GLOBALS['calls'] === 1, ';';
    }
}
$leaf = new SharedOld118;
$outside =& $leaf;
$source = [&$leaf];
$copy = $source;
$result = 41;
$calls = 0;
function captureSharedObject118() {
    global $source;
    echo 'P;';
    return $source;
}
function warnSharedObject118($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['source'][1] = 8;
    $GLOBALS['leaf'] = new SharedNew118;
    $GLOBALS['copy'][0]->tag = 9;
    echo 'I:', $GLOBALS['source'][0]->tag === 9, ':', $GLOBALS['outside']->tag === 9, ':', !isset($GLOBALS['copy'][1]), ';';
    $GLOBALS['source'] = [];
    unset($GLOBALS['source'], $GLOBALS['copy'], $GLOBALS['outside'], $GLOBALS['leaf']);
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('warnSharedObject118');
$result = (
    captureSharedObject118()
    <=> $missing
);
echo 'R:', $result === 1, ':', $missing === true, ':', !isset($source), ':', !isset($copy), ':', !isset($outside), ':', !isset($leaf), ':', $calls === 1, ';END;';
''',
    'peer-object-reference-array-greater-target-default': b'''<?php
class LiveOld118 {
    public $tag = 4;
    function __destruct() { echo 'O:', $GLOBALS['result'] === 41, ';'; }
}
class LiveNew118 {
    public $tag = 7;
    function __destruct() { echo 'N:', $GLOBALS['result'] === true, ':', $this->tag === 10, ';'; }
}
$leaf = new LiveOld118;
$target = [&$leaf];
$copy = $target;
$source = 0;
$result = 41;
$calls = 0;
function warnLiveObject118($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS['source'] =& $GLOBALS['target'];
    $GLOBALS['target'][1] = 8;
    $GLOBALS['leaf'] = new LiveNew118;
    $GLOBALS['copy'][0]->tag = 9;
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return false;
}
set_error_handler('warnLiveObject118');
$result = (
    $source
    > $missing
);
echo 'R:', $result === true, ':', $source[0]->tag === 9, ':', $target[1] === 8, ':', $copy[0]->tag === 9, ':', !isset($copy[1]), ':', $calls === 1, ':', $missing === true, ';';
unset($source, $target);
$copy[0]->tag = 10;
echo 'A:', $leaf->tag === 10, ';';
unset($copy);
echo 'K:', $leaf->tag === 10, ';';
unset($leaf);
echo 'END;';
''',
    'peer-object-reference-array-predicates-no-init': b'''<?php
$leaf = new stdClass;
$leaf->tag = 7;
$content = [&$leaf];
$calls = 0;
function warnObjectPredicates118($level, $message, $file, $line) {
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
set_error_handler('warnObjectPredicates118');
$a = $aMissing != ($savedA = $content);
$b = $bMissing < ($savedB = $content);
$c = ($savedC = $content) <= $cMissing;
$d = $dMissing >= ($savedD = $content);
echo 'R:', $a === true, ':', $b === true, ':', $c === false, ':', $d === false, ':', $content[0]->tag === 8, ':', $leaf->tag === 8, ':', $savedA === [], ':', $savedB === [], ':', $savedC === [], ':', $savedD === [], ':', !isset($aMissing), ':', !isset($bMissing), ':', !isset($cMissing), ':', !isset($dMissing), ':', $calls === 4, ';END;';
''',
    'peer-object-reference-array-captured-supplied-throw': b'''<?php
class ThrownReferenceLeaf118 {
    public $tag = 7;
    function __destruct() {
        echo 'D:', $GLOBALS['result'] === 41, ':', $GLOBALS['seen'] === 1, ':', $this->tag === 8, ';';
    }
}
$leaf = new ThrownReferenceLeaf118;
$outside =& $leaf;
$source = [&$leaf];
$exception = new Exception('chosen118');
$result = 41;
$seen = 0;
$calls = 0;
function captureThrownObject118() {
    global $source;
    echo 'P;';
    return $source;
}
function warnThrownObject118($level, $message, $file, $line) {
    global $calls, $exception;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['leaf']->tag = 8;
    $GLOBALS['source'] = [];
    unset($GLOBALS['source'], $GLOBALS['leaf'], $GLOBALS['outside']);
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['seen'] = 1;
    throw $exception;
}
set_error_handler('warnThrownObject118');
try {
    $result = captureThrownObject118() <=> $missing;
    echo 'BAD;';
} catch (Exception $caught) {
    echo 'C:', $caught === $exception, ':', $result === 41, ':', !isset($source), ':', !isset($leaf), ':', !isset($outside), ':', $missing === true, ':', $seen === 1, ':', $calls === 1, ';';
} finally { echo 'F;'; }
echo 'END;';
''',
}
