"""Same missing direct CV: frozen first NULL and current second scalar."""

CASES = {
    'same-forward-equal-string': b'''<?php
function sameEqual102($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['x'] = '0';
    return true;
}
$result = 41;
set_error_handler('sameEqual102');

$result = ($x == $x);
echo 'R:', ($result === false), ':', ($x === '0'), ':', isset($x), ';END;';
''',
    'same-forward-less-string': b'''<?php
function sameLess102($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['x'] = '0';
    return true;
}
$result = 41;
set_error_handler('sameLess102');

$result = ($x < $x);
echo 'R:', ($result === true), ':', ($x === '0'), ':', isset($x), ';END;';
''',
    'same-forward-notequal-zero': b'''<?php
function sameZero102($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ':', ($m === 'Undefined variable $x'), ';';
    $GLOBALS['x'] = 0; return true;
}
$result = 41;
set_error_handler('sameZero102');
$result = ($x != $x);
echo 'R:', ($result === false), ':', ($x === 0), ':', isset($x), ';END;';
''',
    'same-forward-less-equal-false': b'''<?php
function sameFalse102($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', $line, ';';
    $GLOBALS['x'] = 0; return false;
}
$result = 41;
set_error_handler('sameFalse102');
$result = ($x <= $x);
echo 'R:', ($result === true), ':', ($x === 0), ':', isset($x), ';END;';
''',
    'same-forward-still-missing-boundary': b'''<?php
function sameMissing102($n, $m, $file, $line) { echo 'H|'; return true; }
set_error_handler('sameMissing102');
echo 'B|'; $result = ($x == $x); echo ($result === true);
''',
    'same-forward-array-boundary': b'''<?php
function sameArray102($n, $m, $file, $line) { echo 'H|'; $GLOBALS['x'] = []; return true; }
set_error_handler('sameArray102');
echo 'B|'; $result = ($x == $x); echo $result;
''',
}
