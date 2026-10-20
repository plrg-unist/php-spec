"""Forward scalar helpers freeze both missing values across two Warnings."""

CASES = {
    'second-forward-equal': b'''<?php
function secondEqual100($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $left'), ':', ($m === 'Undefined variable $right'), ':', $line, ';';
    if ($m === 'Undefined variable $left') { $GLOBALS['left'] = 9; }
    else { $GLOBALS['right'] = '0'; }
    return true;
}
$result = 41;
set_error_handler('secondEqual100');
$result = ($left == $right);
echo 'R:', ($result === true), ':', ($left === 9), ':', ($right === '0'), ';END;';
''',
    'second-forward-less-unset': b'''<?php
function secondLess100($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $left'), ':', ($m === 'Undefined variable $right'), ':', $line, ';';
    if ($m === 'Undefined variable $left') { unset($GLOBALS['right']); }
    else { $GLOBALS['right'] = '0'; }
    return true;
}
$right = 2; $result = 41;
set_error_handler('secondLess100');
$result = ($left < $right);
echo 'R:', ($result === false), ':', !isset($left), ':', ($right === '0'), ';END;';
''',
    'second-forward-notequal-less-equal-missing': b'''<?php
function secondMissing100($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $left'), ':', ($m === 'Undefined variable $right'), ':', $line, ';';
    return true;
}
set_error_handler('secondMissing100');
$ne = ($left != $right);
$le = ($left <= $right);
echo 'R:', ($ne === false), ':', ($le === true), ':', !isset($left), ':', !isset($right), ';END;';
''',
    'second-forward-less-equal-false': b'''<?php
function secondFalse100($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $left'), ':', ($m === 'Undefined variable $right'), ':', $line, ';';
    if ($m === 'Undefined variable $left') { $GLOBALS['left'] = 9; }
    else { $GLOBALS['right'] = '0'; }
    return false;
}
$result = 41;
set_error_handler('secondFalse100');
$result = ($left <= $right);
echo 'R:', ($result === true), ':', ($left === 9), ':', ($right === '0'), ';END;';
''',
    'second-forward-same-name-boundary': b'''<?php
function secondSame100($n, $m, $file, $line) { echo 'H|'; return true; }
set_error_handler('secondSame100');
echo 'B|'; $result = ($x == $x); echo ($result === true);
''',
    'second-forward-removed-left-boundary': b'''<?php
function secondRemoved100($n, $m, $file, $line) {
    echo 'H|'; unset($GLOBALS['left']); $GLOBALS['right'] = '0'; return true;
}
$left = 0;
set_error_handler('secondRemoved100');
echo 'B|'; $result = ($left == $right); echo ($result === true);
''',
}
