"""Independent flat child arrays in reference entries: COW and last-chain release."""

CASES = {
    'child-alias-shared-inner-cow': b'''<?php
class SharedChildOld119 {
    public $tag = 4;
    function __destruct() { echo 'O:', $GLOBALS['result'] === 41, ';'; }
}
class SharedChildNew119 {
    public $tag = 7;
    function __destruct() { echo 'N:', $GLOBALS['result'] === 41, ':', $this->tag === 9, ':', $GLOBALS['calls'] === 1, ';'; }
}
$leaf = [new SharedChildOld119];
$outside =& $leaf;
$source = [&$leaf];
$copy = $source;
$result = 41;
$calls = 0;
function captureSharedChild119() { global $source; echo 'P;'; return $source; }
function warnSharedChild119($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['source'][1] = 8;
    $GLOBALS['leaf'] = [new SharedChildNew119];
    $GLOBALS['inner'] = $GLOBALS['leaf'];
    $GLOBALS['copy'][0][1] = 9;
    $GLOBALS['inner'][0]->tag = 9;
    echo 'I:', $GLOBALS['source'][0][0]->tag === 9, ':', $GLOBALS['outside'][0]->tag === 9, ':', !isset($GLOBALS['inner'][1]), ':', $GLOBALS['copy'][0][1] === 9, ':', !isset($GLOBALS['copy'][1]), ';';
    $GLOBALS['source'] = [];
    unset($GLOBALS['source'], $GLOBALS['copy'], $GLOBALS['outside'], $GLOBALS['leaf'], $GLOBALS['inner']);
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('warnSharedChild119');
$result = (
    captureSharedChild119()
    <=> $missing
);
echo 'R:', $result === 1, ':', $missing === true, ':', !isset($source), ':', !isset($copy), ':', !isset($outside), ':', !isset($leaf), ':', !isset($inner), ':', $calls === 1, ';END;';
''',
    'child-alias-singleton-inner-cow': b'''<?php
class SingletonChildOld119 {
    public $tag = 4;
    function __destruct() { echo 'O:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', ($GLOBALS['source'] === [] && $GLOBALS['copy'] === []), ';'; }
}
class SingletonChildNew119 {
    public $tag = 7;
    function __destruct() { echo 'N:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', $GLOBALS['source'] === [], ';'; }
}
$leaf = [new SingletonChildOld119];
$source = [&$leaf];
$copy = $source;
unset($leaf);
$result = 41;
$calls = 0;
function captureSingletonChild119() { global $source; echo 'P;'; return $source; }
function warnSingletonChild119($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['source'][0][0] = new SingletonChildNew119;
    $GLOBALS['source'][0][1] = 8;
    echo 'I:', $GLOBALS['source'][0][0]->tag === 7, ':', $GLOBALS['copy'][0][0]->tag === 4, ':', !isset($GLOBALS['copy'][0][1]), ':', !isset($GLOBALS['leaf']), ';';
    $GLOBALS['source'] = [];
    $GLOBALS['copy'] = [];
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('warnSingletonChild119');
$result = captureSingletonChild119() <=> $missing;
echo 'R:', $result === 1, ':', $source === [], ':', $copy === [], ':', !isset($leaf), ':', $missing === true, ':', $calls === 1, ';END;';
''',
    'child-alias-live-default': b'''<?php
class LiveChildOld119 {
    public $tag = 4;
    function __destruct() { echo 'O:', $GLOBALS['result'] === 41, ';'; }
}
class LiveChildNew119 {
    public $tag = 7;
    function __destruct() { echo 'N:', $GLOBALS['result'] === true, ':', $this->tag === 10, ':', $GLOBALS['calls'] === 1, ';'; }
}
$leaf = [new LiveChildOld119];
$target = [&$leaf];
$copy = $target;
$source = 0;
$result = 41;
$calls = 0;
function warnLiveChild119($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS['source'] =& $GLOBALS['target'];
    $GLOBALS['target'][1] = 8;
    $GLOBALS['leaf'] = [new LiveChildNew119];
    $GLOBALS['inner'] = $GLOBALS['leaf'];
    $GLOBALS['copy'][0][1] = 9;
    $GLOBALS['inner'][0]->tag = 9;
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return false;
}
set_error_handler('warnLiveChild119');
$result = (
    $source
    > $missing
);
echo 'R:', $result === true, ':', $source[0][0]->tag === 9, ':', $target[1] === 8, ':', $copy[0][1] === 9, ':', !isset($copy[1]), ':', !isset($inner[1]), ':', $calls === 1, ':', $missing === true, ';';
unset($source, $target, $copy, $inner);
$leaf[0]->tag = 10;
echo 'K:', $leaf[0]->tag === 10, ';';
unset($leaf);
echo 'END;';
''',
    'child-alias-supplied-throw': b'''<?php
class ThrownChild119 {
    public $tag = 7;
    function __destruct() { echo 'D:', $GLOBALS['result'] === 41, ':', $GLOBALS['seen'] === 1, ':', $this->tag === 8, ';'; }
}
$leaf = [new ThrownChild119];
$outside =& $leaf;
$source = [&$leaf];
$exception = new Exception('chosen119');
$result = 41;
$seen = 0;
$calls = 0;
function captureThrownChild119() { global $source; echo 'P;'; return $source; }
function warnThrownChild119($level, $message, $file, $line) {
    global $calls, $exception;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['leaf'][0]->tag = 8;
    $GLOBALS['source'] = [];
    unset($GLOBALS['source'], $GLOBALS['leaf'], $GLOBALS['outside']);
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['seen'] = 1;
    throw $exception;
}
set_error_handler('warnThrownChild119');
try {
    $result = captureThrownChild119() <=> $missing;
    echo 'BAD;';
} catch (Exception $caught) {
    echo 'C:', $caught === $exception, ':', $result === 41, ':', !isset($source), ':', !isset($leaf), ':', !isset($outside), ':', $missing === true, ':', $seen === 1, ':', $calls === 1, ';';
} finally { echo 'F;'; }
echo 'END;';
''',
}
