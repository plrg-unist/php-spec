"""Live-left scalar spaceship operands across a missing-right warning."""

CASES = {
    'right-scalar-tags': b'''<?php
function scalarRightTags90($n, $m, $file, $line) {
    $GLOBALS['x'] = 9; $GLOBALS['left'] = $GLOBALS['next']; return true;
}
set_error_handler('scalarRightTags90');
echo 'B|';
$left = 1; $next = null; echo $left <=> $x, ':'; unset($x);
$left = 1; $next = false; echo $left <=> $x, ':'; unset($x);
$left = 1; $next = true; echo $left <=> $x, ':'; unset($x);
$left = 1; $next = 0; echo $left <=> $x, ':'; unset($x);
$left = 1; $next = 1.5; echo $left <=> $x, ':'; unset($x);
$left = 1; $next = NAN; echo $left <=> $x, ':'; unset($x);
$left = 1; $next = '0'; echo $left <=> $x, ':'; unset($x);
$left = 1; $part = 'request'; $next = $part . '0'; echo $left <=> $x, ';END;';
''',
    'right-false-default': b'''<?php
function scalarRightFalse90($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ';';
    $GLOBALS['x'] = 9; $GLOBALS['left'] = '0'; return false;
}
$left = 0;
set_error_handler('scalarRightFalse90');
$result = ($left <=> $x);
echo 'R:', ($result === 1), ':', ($left === '0'), ':', ($x === 9), ';END;';
''',
    'right-throw': b'''<?php
function scalarRightThrow90($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ';';
    $GLOBALS['x'] = 9; $GLOBALS['left'] = false; throw $GLOBALS['chosen'];
}
$left = 1; $result = 41; $chosen = new Exception('selected');
set_error_handler('scalarRightThrow90');
try { $result = ($left <=> $x); echo 'BAD;'; }
catch (Exception $caught) { echo 'C:', ($caught === $chosen), ':', ($result === 41), ':', ($left === false), ':', ($x === 9), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
    'right-array-boundary': b'''<?php
function scalarRightArray90($n, $m, $file, $line) {
    echo 'H|'; $GLOBALS['x'] = 9; $GLOBALS['left'] = []; return true;
}
$left = 1;
set_error_handler('scalarRightArray90');
echo 'B|'; $result = ($left <=> $x); echo $result;
''',
    'right-live-plain': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", $line, ":", ($m === 'Undefined variable $x'), ";";
    $GLOBALS['x'] = 9;
    $GLOBALS['y'] = 0;
    return true;
}
$y = 2;
set_error_handler('h');
$v = $y <=> $x;
echo "R:", $v, ":", ($v === 0), ":", $x, ":", $y, ";END;";
''',
}
