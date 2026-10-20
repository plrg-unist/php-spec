"""Same CV at greater operators: physical source-right Warning first."""

CASES = {
    'reversed-same-greater-entry': b'''<?php
function reversedSameGreater104($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ':', $GLOBALS['calls'], ';';
    $GLOBALS['x'] = '0';
    return true;
}
$calls = 0; $result = 41;
set_error_handler('reversedSameGreater104');
$result = ($x > $x);
echo 'R:', ($result === true), ':', ($calls === 1), ':', ($x === '0'), ';END;';
''',
    'reversed-same-greater-equal-second': b'''<?php
function reversedSameEqual104($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ':', $GLOBALS['calls'], ';';
    if ($GLOBALS['calls'] === 2) { $GLOBALS['x'] = '0'; }
    return true;
}
$calls = 0; $result = 41;
set_error_handler('reversedSameEqual104');
$result = ($x >= $x);
echo 'R:', ($result === true), ':', ($calls === 2), ':', ($x === '0'), ';END;';
''',
    'reversed-same-greater-equal-false': b'''<?php
function reversedSameFalse104($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['x'] = '0';
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    return false;
}
$calls = 0; $result = 41;
set_error_handler('reversedSameFalse104');
$result = ($x >= $x);
echo 'R:', ($result === true), ':', ($calls === 1), ':', ($x === '0'), ';END;';
''',
    'reversed-same-greater-greater-equal-missing': b'''<?php
function reversedSameMissing104($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ':', $GLOBALS['calls'], ';';
    return true;
}
$calls = 0; set_error_handler('reversedSameMissing104');
$gt = ($x > $x);
$ge = ($x >= $x);
echo 'R:', ($gt === false), ':', ($ge === true), ':', !isset($x), ':', ($calls === 4), ';END;';
''',
    'reversed-same-greater-second-throw': b'''<?php
function reversedSameThrow104($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ':', $GLOBALS['calls'], ';';
    if ($GLOBALS['calls'] === 2) { throw $GLOBALS['chosen']; } return true;
}
$calls = 0; $result = 41; $chosen = new Exception('chosen104');
set_error_handler('reversedSameThrow104');
try { $result = ($x > $x); echo 'BAD;'; }
catch (Exception $caught) { echo 'C:', ($caught === $chosen), ':', ($result === 41), ':', !isset($x), ':', ($calls === 2), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
    'reversed-same-first-array-boundary': b'''<?php
function reversedSameArray104($n, $m, $file, $line) { echo 'H|'; $GLOBALS['x'] = []; return true; }
set_error_handler('reversedSameArray104');
echo 'B|'; $result = ($x >= $x); echo $result;
''',
}
