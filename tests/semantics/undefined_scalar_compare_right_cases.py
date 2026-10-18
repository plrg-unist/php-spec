"""Live scalar left CVs across missing-right ==/< warnings."""

CASES = {
    'right-equal-live-plain': b'''<?php
function scalarRightEqual92($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['x'] = 9;
    $GLOBALS['left'] = 0;
    return true;
}
$left = 2;
set_error_handler('scalarRightEqual92');
$result = $left == $x;
echo 'R:', ($result === true), ':', ($x === 9), ':', ($left === 0), ';END;';
''',
    'right-less-live-string': b'''<?php
function scalarRightLess92($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['x'] = 9;
    $GLOBALS['left'] = '0';
    return true;
}
$left = 0;
set_error_handler('scalarRightLess92');
$result = $left < $x;
echo 'R:', ($result === false), ':', ($x === 9), ':', ($left === '0'), ';END;';
''',
    'right-scalar-tags-equality': b'''<?php
function scalarRightTags92($n, $m, $file, $line) {
    $GLOBALS['left'] = $GLOBALS['next']; return true;
}
set_error_handler('scalarRightTags92');
echo 'B|';
$part = 'request'; $left = 1; $next = null; echo ($left == $x) ? 'T' : 'F', ':';
$part = 'request'; $left = 1; $next = false; echo ($left == $x) ? 'T' : 'F', ':';
$part = 'request'; $left = 1; $next = true; echo ($left == $x) ? 'T' : 'F', ':';
$part = 'request'; $left = 1; $next = 0; echo ($left == $x) ? 'T' : 'F', ':';
$part = 'request'; $left = 1; $next = 1.5; echo ($left == $x) ? 'T' : 'F', ':';
$part = 'request'; $left = 1; $next = NAN; echo ($left == $x) ? 'T' : 'F', ':';
$part = 'request'; $left = 1; $next = '0'; echo ($left == $x) ? 'T' : 'F', ':';
$part = 'request'; $left = 1; $next = $part . '0'; echo ($left == $x) ? 'T' : 'F', ':';
echo !isset($x), ';END;';
''',
    'right-less-false-default': b'''<?php
function scalarRightFalse92($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ';';
    $GLOBALS['x'] = 9; $GLOBALS['left'] = '0'; return false;
}
$left = 0;
set_error_handler('scalarRightFalse92');
$result = ($left < $x);
echo 'R:', ($result === false), ':', ($left === '0'), ':', ($x === 9), ';END;';
''',
    'right-equal-throw': b'''<?php
function scalarRightThrow92($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ';';
    $GLOBALS['x'] = 9; $GLOBALS['left'] = false; throw $GLOBALS['chosen'];
}
$left = 1; $result = 41; $chosen = new Exception('selected');
set_error_handler('scalarRightThrow92');
try { $result = ($left == $x); echo 'BAD;'; }
catch (Exception $caught) { echo 'C:', ($caught === $chosen), ':', ($result === 41), ':', ($left === false), ':', ($x === 9), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
    'left-array-boundary': b'''<?php
function scalarLeftArray92($n, $m, $file, $line) {
    echo 'H|'; $GLOBALS['x'] = 9; $GLOBALS['left'] = []; return true;
}
$left = 1;
set_error_handler('scalarLeftArray92');
echo 'B|'; $result = ($left == $x); echo $result;
''',
}
