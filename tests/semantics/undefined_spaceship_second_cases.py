"""Second spaceship Warning freezes each missing CV before callbacks."""

CASES = {
    'second-spaceship-string': b'''<?php
function secondString99($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $left'), ':', ($m === 'Undefined variable $right'), ':', $line, ';';
    if ($m === 'Undefined variable $left') { $GLOBALS['left'] = 9; }
    else { $GLOBALS['right'] = '0'; }
    return true;
}
$result = 41;
set_error_handler('secondString99');
$result = ($left <=> $right);
echo 'R:', ($result === 0), ':', ($left === 9), ':', ($right === '0'), ';END;';
''',
    'second-spaceship-unset': b'''<?php
function secondUnset99($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $left'), ':', ($m === 'Undefined variable $right'), ':', $line, ';';
    if ($m === 'Undefined variable $left') { unset($GLOBALS['right']); }
    else { $GLOBALS['right'] = 0; }
    return true;
}
$right = 2; $result = 41;
set_error_handler('secondUnset99');
$result = ($left <=> $right);
echo 'R:', ($result === 0), ':', !isset($left), ':', ($right === 0), ';END;';
''',
    'second-spaceship-still-missing': b'''<?php
function secondMissing99($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $left'), ':', ($m === 'Undefined variable $right'), ':', $line, ';';
    return true;
}
set_error_handler('secondMissing99');
$result = ($left <=> $right);
echo 'R:', ($result === 0), ':', !isset($left), ':', !isset($right), ';END;';
''',
    'second-spaceship-same-false': b'''<?php
function secondFalse99($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ':', $GLOBALS['calls'], ';';
    if ($GLOBALS['calls'] === 2) { $GLOBALS['x'] = true; }
    return $GLOBALS['calls'] === 1;
}
$calls = 0; $result = 41;
set_error_handler('secondFalse99');
$result = ($x <=> $x);
echo 'R:', ($result === 0), ':', ($x === true), ':', ($calls === 2), ';END;';
''',
    'second-spaceship-throw': b'''<?php
function secondThrow99($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $left'), ':', ($m === 'Undefined variable $right'), ':', $line, ';';
    if ($m === 'Undefined variable $right') { throw $GLOBALS['chosen']; }
    return true;
}
$chosen = new Exception('selected'); $result = 41;
set_error_handler('secondThrow99');
try { $result = ($left <=> $right); echo 'BAD;'; }
catch (Exception $caught) { echo 'C:', ($caught === $chosen), ':', ($result === 41), ':', !isset($left), ':', !isset($right), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
    'second-spaceship-removed-left-boundary': b'''<?php
function secondRemoved99($n, $m, $file, $line) {
    echo 'H|'; unset($GLOBALS['left']); $GLOBALS['right'] = 9; return true;
}
$left = 0;
set_error_handler('secondRemoved99');
echo 'B|'; $result = ($left <=> $right); echo $result;
''',
}
