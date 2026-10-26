"""Independent originals for descendant ALIAS cells in comparison array graphs."""

CASES = {
    'reference-graph-singleton-descendant-cow': br'''<?php
class SingleRefOld122 {
    public $tag = 4;
    function __destruct() { echo 'O:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', $this->tag === 8, ':', $GLOBALS['source'] === [], ':', $GLOBALS['copy'] === [], ';'; }
}
class SingleRefNew122 {
    public $tag = 7;
    function __destruct() { echo 'N:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', $this->tag === 7, ':', $GLOBALS['source'] === [], ':', $GLOBALS['copy'][0][0][1] === 4, ';'; }
}
$payload = [new SingleRefOld122, 4];
$branch = [&$payload];
$source = [$branch];
$copy = $source;
unset($branch, $payload);
$result = 41;
$calls = 0;
function captureSingleRef122() { global $source; echo 'P;'; return $source; }
function warnSingleRef122($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['source'][0][0][1] = 9;
    $GLOBALS['source'][0][0][0] = new SingleRefNew122;
    $GLOBALS['copy'][0][0][0]->tag = 8;
    echo 'I:', $GLOBALS['source'][0][0][1] === 9, ':', $GLOBALS['copy'][0][0][1] === 4, ':', $GLOBALS['source'][0][0][0] instanceof SingleRefNew122, ':', $GLOBALS['copy'][0][0][0]->tag === 8, ';';
    $GLOBALS['source'] = [];
    $GLOBALS['copy'] = [];
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('warnSingleRef122');
/* COMPARE */ $result = captureSingleRef122() <=> $missing;
echo 'R:', $result === 1, ':', $missing === true, ':', $calls === 1, ':', $source === [], ':', $copy === [], ';END;';
''',
    'reference-graph-shared-descendant-replacement': br'''<?php
class SharedRefOld122 {
    public $tag = 4;
    function __destruct() { echo 'O:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', $this->tag === 4, ';'; }
}
class SharedRefNew122 {
    public $tag = 7;
    function __destruct() { echo 'N:', $GLOBALS['result'] === 1, ':', $GLOBALS['calls'] === 1, ':', $this->tag === 10, ':', !isset($GLOBALS['outside']), ';'; }
}
$leaf = [new SharedRefOld122, 4];
$outside =& $leaf;
$branch = [&$leaf, &$leaf];
$source = [$branch];
$copy = $source;
$held = $leaf;
unset($branch);
$result = 41;
$calls = 0;
function captureSharedRef122() { global $source; echo 'P;'; return $source; }
function warnSharedRef122($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['source'][1] = 8;
    $GLOBALS['leaf'] = [new SharedRefNew122, 7];
    $GLOBALS['snapshot'] = $GLOBALS['leaf'];
    $GLOBALS['copy'][0][0][1] = 9;
    $GLOBALS['snapshot'][0]->tag = 10;
    echo 'I:', $GLOBALS['source'][1] === 8, ':', !isset($GLOBALS['copy'][1]), ':', $GLOBALS['outside'][1] === 9, ':', $GLOBALS['snapshot'][1] === 7, ':', $GLOBALS['source'][0][1][1] === 9, ':', $GLOBALS['outside'][0]->tag === 10, ':', $GLOBALS['held'][1] === 4, ';';
    $GLOBALS['held'] = [];
    $GLOBALS['source'] = [];
    unset($GLOBALS['source'], $GLOBALS['copy'], $GLOBALS['leaf']);
    $GLOBALS['snapshot'] = [];
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('warnSharedRef122');
/* COMPARE */ $result = captureSharedRef122() <=> $missing;
echo 'R:', $result === 1, ':', !isset($source), ':', !isset($copy), ':', !isset($leaf), ':', $calls === 1, ';';
echo 'A:', $outside[1] === 9, ':', $outside[0]->tag === 10, ':', $snapshot === [], ';';
unset($outside);
echo 'END;';
''',
    'reference-graph-live-default': br'''<?php
$leaf = [4];
$branch = [&$leaf];
$outside =& $leaf;
$copy = [$branch];
unset($branch);
$source = 0;
$result = 41;
$calls = 0;
function warnLiveRef122($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['source'] = $GLOBALS['copy'];
    $GLOBALS['outside'] = [9];
    echo 'I:', $GLOBALS['source'][0][0][0] === 9, ':', $GLOBALS['copy'][0][0][0] === 9, ':', $GLOBALS['outside'][0] === 9, ';';
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return false;
}
set_error_handler('warnLiveRef122');
/* COMPARE */ $result = $source > $missing;
echo 'R:', $result === true, ':', $source[0][0][0] === 9, ':', $copy[0][0][0] === 9, ':', $outside[0] === 9, ':', $missing === true, ':', $calls === 1, ';';
unset($source, $copy, $leaf, $outside);
echo 'END;';
''',
    'reference-graph-supplied-throw': br'''<?php
class ThrowRefLeaf122 {
    public $tag = 4;
    function __destruct() { echo 'D:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', $this->tag === 8, ':', !isset($GLOBALS['source']), ':', !isset($GLOBALS['payload']), ':', !isset($GLOBALS['outside']), ';'; }
}
$payload = [new ThrowRefLeaf122, 4];
$outside =& $payload;
$branch = [&$payload, &$payload];
$source = [$branch];
unset($branch);
$exception = new Exception('chosen-reference-graph-122', 122);
$result = 41;
$calls = 0;
$seen = 0;
function captureThrowRef122() { global $source; echo 'P;'; return $source; }
function warnThrowRef122($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['source'][0][1][0]->tag = 8;
    $GLOBALS['source'] = [];
    unset($GLOBALS['source'], $GLOBALS['payload'], $GLOBALS['outside']);
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['seen'] = 1;
    throw $GLOBALS['exception'];
}
set_error_handler('warnThrowRef122');
try { /* COMPARE */ $result = captureThrowRef122() <=> $missing; }
catch (Exception $caught) {
    echo 'C:', $caught === $exception, ':', $result === 41, ':', $caught->getMessage() === 'chosen-reference-graph-122', ':', $caught->getCode() === 122, ':', !isset($source), ':', !isset($payload), ':', !isset($outside), ':', $calls === 1, ':', $seen === 1, ';';
}
finally { echo 'F;'; }
echo 'END;';
''',
}
