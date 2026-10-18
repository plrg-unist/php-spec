"""Distinct direct-CV comparisons where the first handler defines missing right."""

CASES = {
    'equal-both-init': b'''<?php
function scalarBothEqual95($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['x'] = 9;
    $GLOBALS['right'] = 0;
    return true;
}
$result = 41;
set_error_handler('scalarBothEqual95');
$result = $x == $right;
echo 'R:', ($result === true), ':', ($x === 9), ':', ($right === 0), ';END;';
''',
    'not-equal-both-init': b'''<?php
function scalarNotEqual95($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['right'] = '0';
    return true;
}
$result = 41;
set_error_handler('scalarNotEqual95');
$result = $x != $right;
echo 'R:', ($result === true), ':', !isset($x), ':', ($right === '0'), ';END;';
''',
    'less-both-init': b'''<?php
function scalarBothLess95($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['x'] = 9;
    $GLOBALS['right'] = '0';
    return true;
}
$result = 41;
set_error_handler('scalarBothLess95');
$result = $x < $right;
echo 'R:', ($result === true), ':', ($x === 9), ':', ($right === '0'), ';END;';
''',
    'less-equal-both-false': b'''<?php
function scalarBothFalse95($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ';';
    $GLOBALS['x'] = 9; $GLOBALS['right'] = '0'; return false;
}
$result = 41;
set_error_handler('scalarBothFalse95');
$result = ($x <= $right);
echo 'R:', ($result === true), ':', ($right === '0'), ':', ($x === 9), ';END;';
''',
    'equal-both-throw': b'''<?php
function scalarBothThrow95($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ';';
    throw $GLOBALS['chosen'];
}
$result = 41; $chosen = new Exception('selected');
set_error_handler('scalarBothThrow95');
try { $result = ($x == $right); echo 'BAD;'; }
catch (Exception $caught) { echo 'C:', ($caught === $chosen), ':', ($result === 41), ':', !isset($right), ':', !isset($x), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
    'equal-both-array-boundary': b'''<?php
function scalarNotEqualArray95($n, $m, $file, $line) {
    echo 'H|'; $GLOBALS['x'] = 9; $GLOBALS['right'] = []; return true;
}
$result = 41;
set_error_handler('scalarNotEqualArray95');
echo 'B|'; $result = ($x == $right); echo $result;
''',
}
