"""Recursive DIRECT array DAGs at missing comparison reads."""
CASES = {
    'direct-graph-captured-depth-four': b'''<?php
class OldDirectGraph120 {
    public function __destruct() { echo 'O:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', ($GLOBALS['saved'] === [] && $GLOBALS['copy'] === []), ';'; }
}
class NewDirectGraph120 {
    public function __destruct() { echo 'N:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', ($GLOBALS['saved'] === [] && $GLOBALS['copy'][0][0][0][1] === 4), ';'; }
}
$leaf = [new OldDirectGraph120(), 4];
$shared = [$leaf, $leaf];
$branch = [$shared];
$saved = [$branch];
$copy = $saved;
unset($leaf, $shared, $branch);
$result = 41;
$calls = 0;
function captureDirectGraph120() { echo 'P;'; return $GLOBALS['saved']; }
function warnDirectGraph120($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['saved'][0][0][0][1] = 9;
    $GLOBALS['saved'][0][0][0][0] = new NewDirectGraph120();
    echo 'I:', $GLOBALS['saved'][0][0][0][1] === 9, ':', $GLOBALS['saved'][0][0][1][1] === 4, ':', $GLOBALS['copy'][0][0][0][1] === 4, ':', $GLOBALS['saved'][0][0][0][0] instanceof NewDirectGraph120, ':', $GLOBALS['saved'][0][0][1][0] === $GLOBALS['copy'][0][0][0][0], ';';
    $GLOBALS['saved'] = [];
    $GLOBALS['copy'] = [];
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('warnDirectGraph120');
$result = captureDirectGraph120() <=> $missing;
echo 'R:', $result === 1, ':', $saved === [], ':', $copy === [], ':', $missing === true, ':', $calls === 1, ';END;';
''',
    'direct-graph-live-root-alias': b'''<?php
class OldLiveDirect120 {
    public function __destruct() { echo 'O:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', ($GLOBALS['right'][0][0][1] === 7 && $GLOBALS['held'] === [] && $GLOBALS['copy'] === []), ';'; }
}
class NewLiveDirect120 {
    public function __destruct() { echo 'N:', $GLOBALS['result'] === false, ':', $GLOBALS['calls'] === 1, ':', !isset($GLOBALS['outside']), ';'; }
}
$leaf = [new OldLiveDirect120(), 4];
$shared = [$leaf, $leaf];
$right = [$shared];
$outside =& $right;
$copy = $right;
$held = $right;
unset($leaf, $shared);
$result = 41;
$calls = 0;
function warnLiveDirect120($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['right'] = [[[new NewLiveDirect120(), 7]]];
    echo 'I:', $GLOBALS['held'][0][0][1] === 4, ':', $GLOBALS['copy'][0][1][1] === 4, ':', $GLOBALS['right'][0][0][0] instanceof NewLiveDirect120, ':', $GLOBALS['outside'][0][0][1] === 7, ';';
    $GLOBALS['copy'] = [];
    $GLOBALS['held'] = [];
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('warnLiveDirect120');
$result = $missing == $right;
echo 'R:', $result === false, ':', $right === $outside, ':', ($copy === [] && $held === []), ':', $calls === 1, ':', $missing === true, ';';
unset($right);
echo 'A:', !isset($right), ':', $outside[0][0][0] instanceof NewLiveDirect120, ';';
unset($outside);
echo 'END;';
''',
    'direct-graph-created-pooled-shared-both': b'''<?php
$leaf = [null, false, 7, 1.5, 'bytes'];
$shared = [$leaf, $leaf];
$deep = [$shared, $shared];
$calls = 0;
function createDirectGraph120($level, $message, $file, $line) {
    global $calls, $deep;
    $calls = $calls + 1;
    if ($calls === 1) { $GLOBALS['x'] = [$deep]; }
    else { $GLOBALS['right'] = [$deep]; }
    echo 'H:', $level === 2, ':', ($message === 'Undefined variable $x' || $message === 'Undefined variable $left'), ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('createDirectGraph120');
$a = $x > $x;
$b = $left <=> $right;
echo 'R:', $a === true, ':', $b === -1, ':', $calls === 2, ':', $x[0] === $deep, ':', $right[0] === $deep, ':', !isset($left), ';END;';
''',
    'direct-graph-empty-dag-predicates': b'''<?php
$bottom = [];
$middle = [$bottom, $bottom];
$content = [$middle, $middle];
$calls = 0;
function directPredicates120($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS['content'][0][0][0] = $calls;
    if ($calls === 1) { $GLOBALS['savedA'] = []; }
    elseif ($calls === 2) { $GLOBALS['savedB'] = []; }
    elseif ($calls === 3) { $GLOBALS['savedC'] = []; }
    else { $GLOBALS['savedD'] = []; }
    echo 'H:', $level === 2, ':', ($message === 'Undefined variable $aMissing' || $message === 'Undefined variable $bMissing' || $message === 'Undefined variable $cMissing' || $message === 'Undefined variable $dMissing'), ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('directPredicates120');
$a = $aMissing != ($savedA = $content);
$b = $bMissing < ($savedB = $content);
$c = ($savedC = $content) <= $cMissing;
$d = $dMissing >= ($savedD = $content);
echo 'R:', $a === true, ':', $b === true, ':', $c === false, ':', $d === false, ':', $content[0][0][0] === 4, ':', $content[1][1] === [], ':', $middle[0] === [], ':', $bottom === [], ':', ($savedA === [] && $savedB === [] && $savedC === [] && $savedD === []), ':', $calls === 4, ';END;';
''',
    'direct-graph-live-greater-default': b'''<?php
$leaf = [7];
$tree = [$leaf, $leaf];
$left = 0;
$calls = 0;
function defaultDirect120($level, $message, $file, $line) {
    global $calls, $tree;
    $calls = $calls + 1;
    $GLOBALS['left'] = [$tree, $tree];
    $GLOBALS['left'][0][0][0] = 9;
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return false;
}
set_error_handler('defaultDirect120');
$result = $left > $missing;
echo 'R:', $result === true, ':', $left[0][0][0] === 9, ':', $left[1][0][0] === 7, ':', $tree[0][0] === 7, ':', $missing === true, ':', $calls === 1, ';END;';
''',
    'direct-graph-captured-greater-throw': b'''<?php
class ThrownDirect120 {
    public function __destruct() { echo 'D:', $GLOBALS['result'] === 41, ':', $GLOBALS['seen'] === 1, ';'; }
}
$leaf = [new ThrownDirect120()];
$tree = [$leaf, $leaf];
$content = [$tree, $tree];
unset($leaf, $tree);
$exception = new Exception('chosen120');
$result = 41;
$calls = 0;
$seen = 0;
function throwDirect120($level, $message, $file, $line) {
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
set_error_handler('throwDirect120');
try {
    $result = $missing > ($saved = $content);
    echo 'BAD;';
} catch (Exception $caught) {
    echo 'C:', $caught === $exception, ':', $result === 41, ':', !isset($content), ':', !isset($saved), ':', $missing === true, ':', $calls === 1, ';';
} finally { echo 'F;'; }
echo 'END;';
''',
    'direct-graph-child-alias-ingress-boundary': b'''<?php
$inner = 7;
$leaf = [&$inner];
$right = [$leaf];
set_error_handler(function () { echo 'H|'; return true; });
echo 'B|';
$result = $missing <=> $right;
echo $result;
''',
    'direct-graph-flat-alias-resume-boundary': b'''<?php
$leaf = [7];
$right = [&$leaf];
set_error_handler(function () { echo 'H|'; $GLOBALS['leaf'] = [[8]]; return true; });
echo 'B|';
$result = $missing <=> $right;
echo $result;
''',
}
