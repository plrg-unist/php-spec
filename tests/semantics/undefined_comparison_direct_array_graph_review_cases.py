"""Independent shared DIRECT DAGs, deep COW and final release."""

CASES = {
    'direct-dag-captured-cow': b'''<?php
class CapturedDagOld120 {
    public $tag = 4;
    function __destruct() { echo 'O:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', $this->tag === 8, ':', ($GLOBALS['source'] === [] && $GLOBALS['copy'] === []), ';'; }
}
class CapturedDagNew120 {
    public $tag = 7;
    function __destruct() { echo 'N:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', $this->tag === 7, ':', $GLOBALS['source'] === [], ':', $GLOBALS['copy'][0][0][0][1] === 4, ';'; }
}
$leaf = [new CapturedDagOld120, 4];
$middle = [$leaf, $leaf];
$branch = [$middle];
$source = [$branch, $branch];
$copy = $source;
unset($leaf, $middle, $branch);
$result = 41;
$calls = 0;
function captureDirectDag120() { global $source; echo 'P;'; return $source; }
function warnDirectDag120($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['source'][0][0][0][1] = 9;
    $GLOBALS['source'][0][0][0][0] = new CapturedDagNew120;
    $GLOBALS['copy'][0][0][0][0]->tag = 8;
    echo 'I:', $GLOBALS['source'][0][0][0][1] === 9, ':', $GLOBALS['source'][1][0][0][1] === 4, ':', $GLOBALS['copy'][1][0][1][1] === 4, ':', $GLOBALS['source'][0][0][1][0]->tag === 8, ':', $GLOBALS['source'][0][0][0][0]->tag === 7, ';';
    $GLOBALS['source'] = [];
    $GLOBALS['copy'] = [];
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('warnDirectDag120');
$result = captureDirectDag120() <=> $missing;
echo 'R:', $result === 1, ':', $source === [], ':', $copy === [], ':', $missing === true, ':', $calls === 1, ';END;';
''',
    'direct-graph-live-default': b'''<?php
class LiveGraphOld120 {
    public $tag = 4;
    function __destruct() { echo 'O:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', $GLOBALS['held'] === [], ':', $GLOBALS['source'][0][0][1] === 7, ';'; }
}
class LiveGraphNew120 {
    public $tag = 7;
    function __destruct() { echo 'N:', $GLOBALS['result'] === true, ':', $GLOBALS['calls'] === 1, ':', $this->tag === 10, ':', !isset($GLOBALS['outside']), ';'; }
}
$leaf = [new LiveGraphOld120, 4];
$middle = [$leaf];
$source = [$middle];
$held = $source;
unset($leaf, $middle);
$result = 41;
$calls = 0;
function warnLiveGraph120($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['source'] = [[[new LiveGraphNew120, 7]]];
    $GLOBALS['outside'] = $GLOBALS['source'];
    echo 'I:', $GLOBALS['held'][0][0][1] === 4, ':', $GLOBALS['outside'][0][0][1] === 7, ';';
    $GLOBALS['held'] = [];
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return false;
}
set_error_handler('warnLiveGraph120');
$result = (
    $source
    > $missing
);
echo 'R:', $result === true, ':', $source[0][0][1] === 7, ':', $outside[0][0][1] === 7, ':', $source[0][0][0] === $outside[0][0][0], ':', $held === [], ':', $calls === 1, ':', $missing === true, ';';
unset($source);
$outside[0][0][0]->tag = 10;
$outside[0][0][1] = 10;
echo 'K:', $outside[0][0][1] === 10, ':', $outside[0][0][0]->tag === 10, ';';
unset($outside);
echo 'END;';
''',
    'direct-graph-mixed-flat-alias': b'''<?php
$flat = [5];
$empty = [];
$leaf = [$empty, 4];
$middle = [$leaf, $leaf];
$source = [&$flat, $middle, $middle];
$copy = $source;
unset($empty, $leaf, $middle);
$result = 41;
$calls = 0;
function captureMixedGraph120() { global $source; echo 'P;'; return $source; }
function warnMixedGraph120($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS['flat'][0] = 6;
    $GLOBALS['source'][1][0][0][0] = 9;
    echo 'I:', $GLOBALS['source'][1][0][0][0] === 9, ':', $GLOBALS['source'][2][0][0] === [], ':', $GLOBALS['copy'][1][1][0] === [], ':', $GLOBALS['copy'][0][0] === 6, ':', $GLOBALS['source'][0][0] === 6, ':', $GLOBALS['copy'][1][0][1] === 4, ';';
    $GLOBALS['source'] = [];
    $GLOBALS['copy'] = [];
    unset($GLOBALS['flat']);
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('warnMixedGraph120');
$result = captureMixedGraph120() <=> $missing;
echo 'R:', $result === 1, ':', $source === [], ':', $copy === [], ':', !isset($flat), ':', $missing === true, ':', $calls === 1, ';END;';
''',
    'direct-dag-supplied-throw': b'''<?php
class ThrownDag120 {
    public $tag = 7;
    function __destruct() { echo 'D:', $GLOBALS['result'] === 41, ':', $GLOBALS['seen'] === 1, ':', $this->tag === 8, ';'; }
}
$leaf = [new ThrownDag120, 4];
$middle = [$leaf, $leaf];
$branch = [$middle];
$source = [$branch, $branch];
unset($leaf, $middle, $branch);
$exception = new Exception('chosen120');
$result = 41;
$seen = 0;
$calls = 0;
function captureThrownDag120() { global $source; echo 'P;'; return $source; }
function warnThrownDag120($level, $message, $file, $line) {
    global $calls, $exception;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['source'][0][0][0][0]->tag = 8;
    $GLOBALS['source'] = [];
    unset($GLOBALS['source']);
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['seen'] = 1;
    throw $exception;
}
set_error_handler('warnThrownDag120');
try {
    $result = captureThrownDag120() <=> $missing;
    echo 'BAD;';
} catch (Exception $caught) {
    echo 'C:', $caught === $exception, ':', $result === 41, ':', !isset($source), ':', !isset($leaf), ':', !isset($middle), ':', !isset($branch), ':', $missing === true, ':', $seen === 1, ':', $calls === 1, ';';
} finally { echo 'F;'; }
echo 'END;';
''',
}
