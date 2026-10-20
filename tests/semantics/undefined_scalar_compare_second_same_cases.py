"""Forward same-CV helpers freeze both missing reads across two Warnings."""

CASES = {
    'same-second-equal': b'''<?php
function sameSecondEqual103($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ':', $GLOBALS['calls'], ';';
    if ($GLOBALS['calls'] === 2) { $GLOBALS['x'] = '0'; }
    return true;
}
$calls = 0; $result = 41;
set_error_handler('sameSecondEqual103');
$result = ($x == $x);
echo 'R:', ($result === true), ':', ($calls === 2), ':', ($x === '0'), ';END;';
''',
    'same-second-less-unset': b'''<?php
function sameSecondLess103($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ':', $GLOBALS['calls'], ';';
    if ($GLOBALS['calls'] === 1) { $GLOBALS['x'] = 9; unset($GLOBALS['x']); } else { $GLOBALS['x'] = '0'; }
    return true;
}
$calls = 0; $result = 41;
set_error_handler('sameSecondLess103');
$result = ($x < $x);
echo 'R:', ($result === false), ':', ($calls === 2), ':', ($x === '0'), ';END;';
''',
    'same-second-notequal-less-equal-missing': b'''<?php
function sameSecondMissing103($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ':', $GLOBALS['calls'], ';';
    return true;
}
$calls = 0; set_error_handler('sameSecondMissing103');
$ne = ($x != $x);
$le = ($x <= $x);
echo 'R:', ($ne === false), ':', ($le === true), ':', !isset($x), ':', ($calls === 4), ';END;';
''',
    'same-second-less-equal-false': b'''<?php
function sameSecondFalse103($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ':', $GLOBALS['calls'], ';';
    if ($GLOBALS['calls'] === 2) { $GLOBALS['x'] = true; }
    return false;
}
$calls = 0; $result = 41;
set_error_handler('sameSecondFalse103');
$result = ($x <= $x);
echo 'R:', ($result === true), ':', ($calls === 2), ':', ($x === true), ';END;';
''',
    'same-second-notequal-supplied-throw': b'''<?php
function sameSecondThrow103($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ':', $GLOBALS['calls'], ';';
    if ($GLOBALS['calls'] === 2) { throw $GLOBALS['chosen']; } return true;
}
$calls = 0; $result = 41; $chosen = new Exception('chosen103');
set_error_handler('sameSecondThrow103');
try { $result = ($x != $x); echo 'BAD;'; }
catch (Exception $caught) { echo 'C:', ($caught === $chosen), ':', ($result === 41), ':', !isset($x), ':', ($calls === 2), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
    'same-second-first-array-boundary': b'''<?php
function sameSecondArray103($n, $m, $file, $line) { echo 'H|'; $GLOBALS['x'] = []; return true; }
set_error_handler('sameSecondArray103');
echo 'B|'; $result = ($x == $x); echo $result;
''',
}
