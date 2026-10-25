"""Recursive DIRECT DAG payloads in comparison ALIAS entries."""
CASES = {
    'alias-dag-captured-singleton': b'''<?php
class OldAliasDag121 {
    public function __destruct() { echo 'O:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', ($GLOBALS['saved'] === [] && $GLOBALS['copy'] === []), ';'; }
}
class NewAliasDag121 {
    public function __destruct() { echo 'N:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', ($GLOBALS['saved'] === [] && $GLOBALS['copy'][0][0][0][1] === 4), ';'; }
}
$leaf = [new OldAliasDag121(), 4];
$shared = [$leaf, $leaf];
$payload = [$shared];
$saved = [&$payload];
$copy = $saved;
unset($leaf, $shared, $payload);
$result = 41;
$calls = 0;
function captureAliasDag121() { echo 'P;'; return $GLOBALS['saved']; }
function warnAliasDag121($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['saved'][0][0][0][1] = 9;
    $GLOBALS['saved'][0][0][0][0] = new NewAliasDag121();
    echo 'I:', $GLOBALS['saved'][0][0][0][1] === 9, ':', $GLOBALS['saved'][0][0][1][1] === 4, ':', $GLOBALS['copy'][0][0][0][1] === 4, ':', $GLOBALS['saved'][0][0][0][0] instanceof NewAliasDag121, ':', $GLOBALS['saved'][0][0][1][0] === $GLOBALS['copy'][0][0][0][0], ';';
    $GLOBALS['saved'] = [];
    $GLOBALS['copy'] = [];
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('warnAliasDag121');
$result = captureAliasDag121() <=> $missing;
echo 'R:', $result === 1, ':', $saved === [], ':', $copy === [], ':', $missing === true, ':', $calls === 1, ';END;';
''',
    'alias-dag-live-held-snapshot': b'''<?php
class OldLiveAliasDag121 {
    public function __destruct() { echo 'O:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', ($GLOBALS['payload'][0][0][1] === 7 && $GLOBALS['held'] === [] && $GLOBALS['copy'] === []), ';'; }
}
class NewLiveAliasDag121 {
    public function __destruct() { echo 'N:', $GLOBALS['result'] === false, ':', $GLOBALS['calls'] === 1, ':', !isset($GLOBALS['outside']), ';'; }
}
$leaf = [new OldLiveAliasDag121(), 4];
$shared = [$leaf, $leaf];
$payload = [$shared];
$outside =& $payload;
$right = [&$payload];
$copy = $right;
$held = $payload;
unset($leaf, $shared);
$result = 41;
$calls = 0;
function warnLiveAliasDag121($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'B;';
    $GLOBALS['payload'] = [[[new NewLiveAliasDag121(), 7]]];
    echo 'I:', $GLOBALS['held'][0][0][1] === 4, ':', $GLOBALS['copy'][0][0][0][1] === 7, ':', $GLOBALS['right'][0][0][0][0] instanceof NewLiveAliasDag121, ':', $GLOBALS['outside'][0][0][1] === 7, ';';
    $GLOBALS['copy'] = [];
    $GLOBALS['held'] = [];
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('warnLiveAliasDag121');
$result = $missing == $right;
echo 'R:', $result === false, ':', $right[0] === $outside, ':', ($copy === [] && $held === []), ':', $calls === 1, ':', $missing === true, ';';
unset($right, $payload);
echo 'A:', !isset($right), ':', $outside[0][0][0] instanceof NewLiveAliasDag121, ';';
unset($outside);
echo 'END;';
''',
    'alias-dag-created-pooled-shared-both': b'''<?php
$leaf = [null, false, 7, 1.5, 'bytes'];
$payload = [[$leaf, $leaf]];
$calls = 0;
function createAliasDag121($level, $message, $file, $line) {
    global $calls, $payload;
    $calls = $calls + 1;
    if ($calls === 1) { $GLOBALS['x'] = [&$payload]; }
    else { $GLOBALS['right'] = [&$payload]; }
    echo 'H:', $level === 2, ':', ($message === 'Undefined variable $x' || $message === 'Undefined variable $left'), ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('createAliasDag121');
$a = $x > $x;
$b = $left <=> $right;
echo 'R:', $a === true, ':', $b === -1, ':', $calls === 2, ':', $x[0] === $payload, ':', $right[0] === $payload, ':', !isset($left), ';END;';
''',
    'alias-dag-empty-child-predicates': b'''<?php
$bottom = [];
$payload = [[$bottom, $bottom]];
$content = [&$payload];
$calls = 0;
function predicatesAliasDag121($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS['payload'][0][0][0] = $calls;
    if ($calls === 1) { $GLOBALS['savedA'] = []; }
    elseif ($calls === 2) { $GLOBALS['savedB'] = []; }
    elseif ($calls === 3) { $GLOBALS['savedC'] = []; }
    else { $GLOBALS['savedD'] = []; }
    echo 'H:', $level === 2, ':', ($message === 'Undefined variable $aMissing' || $message === 'Undefined variable $bMissing' || $message === 'Undefined variable $cMissing' || $message === 'Undefined variable $dMissing'), ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('predicatesAliasDag121');
$a = $aMissing != ($savedA = $content);
$b = $bMissing < ($savedB = $content);
$c = ($savedC = $content) <= $cMissing;
$d = $dMissing >= ($savedD = $content);
echo 'R:', $a === true, ':', $b === true, ':', $c === false, ':', $d === false, ':', $payload[0][0][0] === 4, ':', $payload[0][1] === [], ':', $bottom === [], ':', $content[0] === $payload, ':', ($savedA === [] && $savedB === [] && $savedC === [] && $savedD === []), ':', $calls === 4, ';END;';
''',
    'alias-dag-live-greater-default': b'''<?php
$payload = [[7]];
$outside =& $payload;
$array = [&$payload];
$held = $payload;
$left = 0;
$calls = 0;
function defaultAliasDag121($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS['left'] = $GLOBALS['array'];
    $GLOBALS['outside'][0][0] = 9;
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return false;
}
set_error_handler('defaultAliasDag121');
$result = $left > $missing;
echo 'R:', $result === true, ':', $left[0][0][0] === 9, ':', $array[0][0][0] === 9, ':', $held[0][0] === 7, ':', $outside[0][0] === 9, ':', $missing === true, ':', $calls === 1, ';END;';
''',
    'alias-dag-captured-greater-throw': b'''<?php
class ThrowAliasDag121 {
    public function __destruct() { echo 'D:', $GLOBALS['result'] === 41, ':', $GLOBALS['seen'] === 1, ';'; }
}
$leaf = [new ThrowAliasDag121()];
$payload = [[$leaf, $leaf]];
$outside =& $payload;
$content = [&$payload];
unset($leaf);
$exception = new Exception('chosen121');
$result = 41;
$calls = 0;
$seen = 0;
function throwAliasDag121($level, $message, $file, $line) {
    global $calls, $exception;
    $calls = $calls + 1;
    $GLOBALS['content'] = [];
    $GLOBALS['saved'] = [];
    unset($GLOBALS['content'], $GLOBALS['saved'], $GLOBALS['outside'], $GLOBALS['payload']);
    $GLOBALS['missing'] = true;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['seen'] = 1;
    throw $exception;
}
set_error_handler('throwAliasDag121');
try {
    $result = $missing > ($saved = $content);
    echo 'BAD;';
} catch (Exception $caught) {
    echo 'C:', $caught === $exception, ':', $result === 41, ':', !isset($content), ':', !isset($saved), ':', !isset($outside), ':', !isset($payload), ':', $missing === true, ':', $calls === 1, ';';
} finally { echo 'F;'; }
echo 'END;';
''',
    'alias-dag-child-reference-ingress-boundary': b'''<?php
$inner = 7;
$leaf = [&$inner];
$payload = [$leaf];
$right = [&$payload];
set_error_handler(function () { echo 'H|'; return true; });
echo 'B|';
$result = $missing <=> $right;
echo $result;
''',
    'alias-dag-internal-child-resume-boundary': b'''<?php
$payload = [[7]];
$right = [&$payload];
set_error_handler(function () { echo 'H|'; $GLOBALS['payload'] = [[new Exception('internal')]]; return true; });
echo 'B|';
$result = $missing <=> $right;
echo $result;
''',
}
