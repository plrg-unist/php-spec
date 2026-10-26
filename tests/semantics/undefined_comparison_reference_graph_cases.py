"""Original-source witnesses for recursive comparison reference graphs."""

CASES = {
    'reference-graph-captured-shared-branches': br'''<?php
class OldBranchRef122 {
    function __destruct() { $GLOBALS['old'] = $GLOBALS['old'] + 1; echo 'O:', $GLOBALS['inside'] === false, ':', $GLOBALS['result'] === 41, ':', $GLOBALS['missing'] === true, ';'; }
}
class NewBranchRef122 {
    function __destruct() { $GLOBALS['new'] = $GLOBALS['new'] + 1; echo 'N:', $GLOBALS['inside'] === true, ':', $GLOBALS['result'] === 41, ':', $GLOBALS['missing'] === true, ';'; }
}
$leaf = [new OldBranchRef122, 4];
$middle = [&$leaf];
$branch = [&$middle];
$saved = [$branch, $branch];
$copy = $saved;
unset($leaf, $middle, $branch);
$result = 41;
$old = 0;
$new = 0;
$inside = false;
function capturedBranchRef122() { global $saved; echo 'P;'; return $saved; }
function warnBranchRef122($level, $message, $file, $line) {
    $GLOBALS['inside'] = true;
    $GLOBALS['missing'] = true;
    echo 'B;';
    $GLOBALS['copy'][0][0][0][1] = 9;
    echo 'I:', $GLOBALS['saved'][0][0][0][1] === 4, ':', $GLOBALS['saved'][1][0][0][1] === 4, ':', $GLOBALS['copy'][0][0][0][1] === 9, ':', $GLOBALS['copy'][1][0][0][1] === 4, ':', $GLOBALS['copy'][0][0][0][0] === $GLOBALS['saved'][0][0][0][0], ';';
    $GLOBALS['copy'][0][0][0][0] = new NewBranchRef122;
    $GLOBALS['copy'] = [];
    $GLOBALS['saved'] = [];
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $GLOBALS['old'] === 0, ':', $GLOBALS['new'] === 1, ';';
    $GLOBALS['inside'] = false;
    return true;
}
set_error_handler('warnBranchRef122');
/* COMPARE */ $result = capturedBranchRef122() <=> $missing;
echo 'R:', $result === 1, ':', $missing === true, ':', $old === 1, ':', $new === 1, ':', $saved === [], ':', $copy === [], ';END;';
''',
    'reference-graph-live-held-payload': br'''<?php
class OldHeldRef122 {
    function __destruct() { $GLOBALS['old'] = $GLOBALS['old'] + 1; echo 'O:', $GLOBALS['inside'] === true, ':', $GLOBALS['result'] === 41, ':', $GLOBALS['missing'] === true, ';'; }
}
class NewHeldRef122 {
    function __destruct() { $GLOBALS['new'] = $GLOBALS['new'] + 1; echo 'N:', $GLOBALS['inside'] === false, ':', $GLOBALS['result'] === false, ':', $GLOBALS['missing'] === true, ';'; }
}
$leaf = [new OldHeldRef122, 4];
$outside =& $leaf;
$branch = [&$leaf];
$right = [$branch, $branch];
$copy = $right;
$held = $leaf;
unset($leaf, $branch);
$result = 41;
$old = 0;
$new = 0;
$inside = false;
function warnHeldRef122($level, $message, $file, $line) {
    $GLOBALS['inside'] = true;
    $GLOBALS['missing'] = true;
    echo 'B;';
    $GLOBALS['outside'] = [new NewHeldRef122, 7];
    $GLOBALS['copy'][0][0][1] = 8;
    echo 'I:', $GLOBALS['right'][0][0][1] === 8, ':', $GLOBALS['right'][1][0][1] === 8, ':', $GLOBALS['copy'][1][0][1] === 8, ':', $GLOBALS['held'][1] === 4, ':', $GLOBALS['right'][0][0][0] === $GLOBALS['outside'][0], ';';
    $GLOBALS['copy'] = [];
    $GLOBALS['held'] = [];
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $GLOBALS['old'] === 1, ':', $GLOBALS['new'] === 0, ';';
    $GLOBALS['inside'] = false;
    return true;
}
set_error_handler('warnHeldRef122');
/* COMPARE */ $result = $missing == $right;
echo 'R:', $result === false, ':', $old === 1, ':', $new === 0, ':', $outside[1] === 8, ';';
$right = [];
echo 'A:', $new === 0, ':', $outside[1] === 8, ';';
unset($outside);
echo 'END;';
''',

    'reference-graph-created-both-ne': br'''<?php
$payload = [7];
$branch = [&$payload];
$template = [$branch];
unset($branch);
$calls = 0;
function warnBothRef122($level, $message, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $GLOBALS['left'] = true;
    $GLOBALS['right'] = $GLOBALS['template'];
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $left', ';';
    return true;
}
set_error_handler('warnBothRef122');
echo 'B;';
/* COMPARE */ $result = $left != $right;
echo 'R:', $result === true, ':', $left === true, ':', $right[0][0][0] === 7, ':', $calls === 1, ';END;';
''',
    'reference-graph-created-same-pooled-less': br'''<?php
$leaf = [7];
$branch = [&$leaf];
$template = [$branch];
unset($branch);
$calls = 0;
function warnSameRef122($level, $message, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $GLOBALS['leaf'] = [8];
    $GLOBALS['same'] = $GLOBALS['template'];
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $same', ';';
    return true;
}
set_error_handler('warnSameRef122');
echo 'B;';
/* COMPARE */ $result = $same < $same;
echo 'R:', $result === true, ':', $same[0][0][0] === 8, ':', $template[0][0][0] === 8, ':', $calls === 1, ';END;';
''',
    'reference-graph-empty-descendant-le-ge': br'''<?php
$leaf = [];
$branch = [&$leaf];
$array = [$branch];
unset($branch);
$calls = 0;
function warnEmptyRef122($level, $message, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    if ($GLOBALS['calls'] === 1) { $GLOBALS['le_missing'] = true; }
    else { $GLOBALS['ge_missing'] = true; }
    $GLOBALS['leaf'] = [];
    echo 'H:', $level === 2, ';';
    return true;
}
set_error_handler('warnEmptyRef122');
echo 'B;';
/* COMPARE */ $le = $array <= $le_missing;
$ge = $array >= $ge_missing;
echo 'R:', $le === false, ':', $ge === true, ':', $array[0][0] === [], ':', $calls === 2, ':', $le_missing === true, ':', $ge_missing === true, ';END;';
''',
    'reference-graph-captured-ge-throw': br'''<?php
class BooleanRefLeaf122 {
    function __destruct() { echo 'D:', $GLOBALS['result'] === 41, ':', $GLOBALS['calls'] === 1, ':', $GLOBALS['missing'] === true, ':', !isset($GLOBALS['content']), ':', !isset($GLOBALS['saved']), ';'; }
}
$leaf = [new BooleanRefLeaf122, 7];
$branch = [&$leaf];
$content = [$branch];
unset($leaf, $branch);
$exception = new Exception('chosen-boolean-reference-122', 122);
$result = 41;
$calls = 0;
function throwBooleanRef122($level, $message, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $GLOBALS['missing'] = true;
    unset($GLOBALS['content'], $GLOBALS['saved']);
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ';';
    throw $GLOBALS['exception'];
}
set_error_handler('throwBooleanRef122');
echo 'B;';
try {
    /* COMPARE */ $result = $missing >= ($saved = $content);
    echo 'BAD;';
} catch (Exception $caught) {
    echo 'C:', $caught === $exception, ':', $result === 41, ':', $calls === 1, ':', $missing === true, ':', !isset($content), ':', !isset($saved), ';';
} finally { echo 'F;'; }
echo 'END;';
''',
    'reference-graph-two-cell-cycle-resume-boundary': br'''<?php
$payload = [7];
$branch = [&$payload];
$right = [$branch];
function cycleReference122() {
    global $payload, $right;
    echo 'H|';
    $payload = [&$right];
    return true;
}
set_error_handler('cycleReference122');
echo 'B|';
/* COMPARE */ $result = $missing <=> $right;
echo $result;
''',
    'reference-graph-internal-payload-resume-boundary': br'''<?php
$payload = [7];
$branch = [&$payload];
$right = [$branch];
function internalReference122() {
    global $payload;
    echo 'H|';
    $payload = [new Exception('internal-reference-122')];
    return true;
}
set_error_handler('internalReference122');
echo 'B|';
/* COMPARE */ $result = $missing <=> $right;
echo $result;
''',
}
