"""Reversed scalar comparisons freeze both missing values right then left."""

CASES = {
    'second-reversed-greater': b'''<?php
function secondGreater101($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $left'), ':', ($m === 'Undefined variable $right'), ':', $line, ';';
    if ($m === 'Undefined variable $right') { $GLOBALS['right'] = 9; }
    else { $GLOBALS['left'] = '0'; }
    return true;
}
$result = 41;
set_error_handler('secondGreater101');
$result = ($left > $right);
echo 'R:', ($result === false), ':', ($left === '0'), ':', ($right === 9), ';END;';
''',
    'second-reversed-greaterequal-unset': b'''<?php
function secondGreaterEqual101($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $left'), ':', ($m === 'Undefined variable $right'), ':', $line, ';';
    if ($m === 'Undefined variable $right') { unset($GLOBALS['left']); }
    else { $GLOBALS['left'] = '0'; }
    return true;
}
$left = 2; $result = 41;
set_error_handler('secondGreaterEqual101');
$result = ($left >= $right);
echo 'R:', ($result === true), ':', ($left === '0'), ':', !isset($right), ';END;';
''',
    'second-reversed-both-missing': b'''<?php
function secondMissing101($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $left'), ':', ($m === 'Undefined variable $right'), ':', $line, ';';
    return true;
}
set_error_handler('secondMissing101');
$gt = ($left > $right);
$ge = ($left >= $right);
echo 'R:', ($gt === false), ':', ($ge === true), ':', !isset($left), ':', !isset($right), ';END;';
''',
    'second-reversed-greaterequal-false': b'''<?php
function secondFalse101($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $left'), ':', ($m === 'Undefined variable $right'), ':', $line, ';';
    if ($m === 'Undefined variable $right') { $GLOBALS['right'] = 9; }
    else { $GLOBALS['left'] = '0'; }
    return false;
}
$result = 41;
set_error_handler('secondFalse101');
$result = ($left >= $right);
echo 'R:', ($result === true), ':', ($left === '0'), ':', ($right === 9), ';END;';
''',
    'second-reversed-same-name-boundary': b'''<?php
function secondSame101($n, $m, $file, $line) { echo 'H|'; return true; }
set_error_handler('secondSame101');
echo 'B|'; $result = ($x > $x); echo ($result === false);
''',
    'second-reversed-removed-right-boundary': b'''<?php
function secondRemoved101($n, $m, $file, $line) {
    echo 'H|'; unset($GLOBALS['right']); $GLOBALS['left'] = '0'; return true;
}
$right = 0;
set_error_handler('secondRemoved101');
echo 'B|'; $result = ($left > $right); echo ($result === false);
''',
}
