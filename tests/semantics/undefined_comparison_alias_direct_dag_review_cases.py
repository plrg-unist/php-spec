"""Independent originals for deep DIRECT DAGs held by outer ALIAS cells."""

CASES = {
    'alias-dag-singleton-deep-cow': br'''<?php
class SingletonDagOld121 {
    public $tag = 4;
    function __destruct() { echo 'O:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', $this->tag === 8, ':', ($GLOBALS['source'] === [] && $GLOBALS['copy'] === []), ';'; }
}
class SingletonDagNew121 {
    public $tag = 7;
    function __destruct() { echo 'N:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', $this->tag === 7, ':', $GLOBALS['source'] === [], ':', $GLOBALS['copy'][0][0][0][1] === 4, ';'; }
}
$leaf = [new SingletonDagOld121, 4];
$middle = [$leaf, $leaf];
$deep = [$middle];
$source = [&$deep];
$copy = $source;
unset($leaf, $middle, $deep);
$result = 41;
$calls = 0;
function captureSingletonDag121() { global $source; echo 'P;'; return $source; }
function warnSingletonDag121($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['source'][0][0][0][1] = 9;
    $GLOBALS['source'][0][0][0][0] = new SingletonDagNew121;
    $GLOBALS['copy'][0][0][1][0]->tag = 8;
    echo 'I:', $GLOBALS['source'][0][0][0][1] === 9, ':', $GLOBALS['source'][0][0][1][1] === 4, ':', $GLOBALS['copy'][0][0][0][1] === 4, ':', $GLOBALS['source'][0][0][1][0]->tag === 8, ':', $GLOBALS['source'][0][0][0][0] instanceof SingletonDagNew121, ';';
    $GLOBALS['source'] = [];
    $GLOBALS['copy'] = [];
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('warnSingletonDag121');
/* COMPARE */ $result = captureSingletonDag121() <=> $missing;
echo 'R:', $result === 1, ':', $source === [], ':', $copy === [], ':', $missing === true, ':', $calls === 1, ';END;';
''',
    'alias-dag-shared-cell-replacement': br'''<?php
class SharedDagOld121 {
    public $tag = 4;
    function __destruct() { echo 'O:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', $this->tag === 4, ';'; }
}
class SharedDagNew121 {
    public $tag = 7;
    function __destruct() { echo 'N:', $GLOBALS['result'] === 1, ':', $GLOBALS['calls'] === 1, ':', $this->tag === 10, ':', !isset($GLOBALS['outside']), ';'; }
}
$leaf = [new SharedDagOld121, 4];
$deep = [[$leaf, $leaf]];
$outside =& $deep;
$held = $deep;
$source = [&$deep];
$copy = $source;
unset($leaf);
$result = 41;
$calls = 0;
function captureSharedDag121() { global $source; echo 'P;'; return $source; }
function warnSharedDag121($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['source'][1] = 8;
    $fresh = [new SharedDagNew121, 7];
    $GLOBALS['deep'] = [[$fresh, $fresh]];
    unset($fresh);
    $GLOBALS['inner'] = $GLOBALS['deep'];
    $GLOBALS['copy'][0][0][0][1] = 9;
    $GLOBALS['inner'][0][0][0]->tag = 10;
    echo 'I:', $GLOBALS['source'][1] === 8, ':', !isset($GLOBALS['copy'][1]), ':', $GLOBALS['outside'][0][0][1] === 9, ':', $GLOBALS['outside'][0][1][1] === 7, ':', $GLOBALS['inner'][0][0][1] === 7, ':', $GLOBALS['outside'][0][1][0]->tag === 10, ':', $GLOBALS['held'][0][0][1] === 4, ';';
    $GLOBALS['held'] = [];
    $GLOBALS['source'] = [];
    unset($GLOBALS['source'], $GLOBALS['copy'], $GLOBALS['deep']);
    $GLOBALS['inner'] = [];
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('warnSharedDag121');
/* COMPARE */ $result = captureSharedDag121() <=> $missing;
echo 'R:', $result === 1, ':', !isset($source), ':', !isset($copy), ':', !isset($deep), ':', $calls === 1, ';';
echo 'A:', $outside[0][0][1] === 9, ':', $outside[0][1][1] === 7, ':', $outside[0][0][0]->tag === 10, ';';
unset($outside);
echo 'END;';
''',
    'alias-dag-live-default': br'''<?php
$leaf = [4];
$deep = [[$leaf, $leaf]];
$outside =& $deep;
$copy = [&$deep];
unset($leaf);
$source = 0;
$result = 41;
$calls = 0;
function warnLiveDag121($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['source'] = $GLOBALS['copy'];
    $GLOBALS['outside'][0][0][0] = 9;
    echo 'I:', $GLOBALS['source'][0][0][0][0] === 9, ':', $GLOBALS['source'][0][0][1][0] === 4, ':', $GLOBALS['copy'][0][0][0][0] === 9, ':', $GLOBALS['outside'][0][0][0] === 9, ';';
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return false;
}
set_error_handler('warnLiveDag121');
/* COMPARE */ $result = $source > $missing;
echo 'R:', $result === true, ':', $source[0][0][0][0] === 9, ':', $source[0][0][1][0] === 4, ':', $copy[0][0][0][0] === 9, ':', $missing === true, ':', $calls === 1, ';';
unset($source, $copy, $deep, $outside);
echo 'END;';
''',
    'alias-dag-supplied-throw': br'''<?php
class ThrowDagLeaf121 {
    public $tag = 4;
    function __destruct() { echo 'D:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', $this->tag === 8, ':', !isset($GLOBALS['source']), ':', !isset($GLOBALS['deep']), ':', !isset($GLOBALS['outside']), ';'; }
}
$leaf = [new ThrowDagLeaf121, 4];
$deep = [[$leaf, $leaf]];
$outside =& $deep;
$source = [&$deep];
unset($leaf);
$result = 41;
$calls = 0;
$exception = new Exception('chosen-alias-dag-121', 121);
function captureThrowDag121() { global $source; echo 'P;'; return $source; }
function warnThrowDag121($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['outside'][0][0][0]->tag = 8;
    $GLOBALS['source'] = [];
    unset($GLOBALS['source'], $GLOBALS['deep'], $GLOBALS['outside']);
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['seen'] = 1;
    throw $GLOBALS['exception'];
}
set_error_handler('warnThrowDag121');
try {
    /* COMPARE */ $result = captureThrowDag121() <=> $missing;
    echo 'BAD;';
} catch (Exception $caught) {
    echo 'C:', $caught === $exception, ':', $result === 41, ':', $caught->getMessage() === 'chosen-alias-dag-121', ':', $caught->getCode() === 121, ':', !isset($source), ':', !isset($deep), ':', !isset($outside), ':', $calls === 1, ':', $seen === 1, ';';
} finally { echo 'F;'; }
echo 'END;';
''',
}
