"""Both-missing spaceship comparisons freeze NULL before a current right read."""

CASES = {
    'both-spaceship-string': b'''<?php
function scalarBothSpaceship97($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['x'] = 9;
    $GLOBALS['right'] = '0';
    return true;
}
$result = 41;
set_error_handler('scalarBothSpaceship97');
$result = $x <=> $right;
echo 'R:', ($result === -1), ':', ($x === 9), ':', ($right === '0'), ';END;';
''',
    'both-spaceship-zero-first-absent': b'''<?php
function scalarBothSpaceshipZero97($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['right'] = 0;

    return true;
}
$result = 41;
set_error_handler('scalarBothSpaceshipZero97');
$result = $x <=> $right;
echo 'R:', ($result === 0), ':', !isset($x), ':', ($right === 0), ';END;';
''',
    'both-spaceship-boolean': b'''<?php
function scalarBothBool97($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['x'] = 9; $GLOBALS['right'] = true; return true;
}
$result = 41;
set_error_handler('scalarBothBool97');
$result = ($x <=> $right);
echo 'R:', ($result === -1), ':', ($right === true), ':', ($x === 9), ';END;';
''',
    'both-spaceship-false': b'''<?php
function scalarBothFalse97($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ';';
    $GLOBALS['x'] = 9; $GLOBALS['right'] = '0'; return false;
}
$result = 41;
set_error_handler('scalarBothFalse97');
$result = ($x <=> $right);
echo 'R:', ($result === -1), ':', ($right === '0'), ':', ($x === 9), ';END;';
''',
    'both-spaceship-throw': b'''<?php
function scalarBothThrow97($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ';';
    throw $GLOBALS['chosen'];
}
$result = 41; $chosen = new Exception('selected');
set_error_handler('scalarBothThrow97');
try { $result = ($x <=> $right); echo 'BAD;'; }
catch (Exception $caught) { echo 'C:', ($caught === $chosen), ':', ($result === 41), ':', !isset($right), ':', !isset($x), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
    'both-spaceship-array-boundary': b'''<?php
function scalarBothArray97($n, $m, $file, $line) {
    echo 'H|'; $GLOBALS['x'] = 9; $GLOBALS['right'] = []; return true;
}
$result = 41;
set_error_handler('scalarBothArray97');
echo 'B|'; $result = ($x <=> $right); echo $result;
''',
}
