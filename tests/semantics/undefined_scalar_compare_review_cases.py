"""Independent scalar comparison warning originals, retained byte-for-byte."""

CASES = {
    'peer-plain-right-mutates-both-ops': b'''<?php
function peerPlainRight91($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    $GLOBALS['missing'] = 9;
    $GLOBALS['right'] = 0;
    return true;
}
$right = 1;
set_error_handler('peerPlainRight91');
$equal = ($missing == $right);
echo 'E:', ($equal === true), ':', ($missing === 9), ':', ($right === 0), ';';
unset($missing); $right = 1;
$less = ($missing < $right);
echo 'L:', ($less === false), ':', ($missing === 9), ':', ($right === 0), ';END;';
''',
    'peer-plain-right-becomes-reference-string': b'''<?php
function peerReferenceRight91($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    $GLOBALS['missing'] = 9;
    $GLOBALS['alias'] =& $GLOBALS['right'];
    $GLOBALS['right'] = '0';
    return true;
}
$right = 0;
set_error_handler('peerReferenceRight91');
$result = ($missing
    ==
    $right);
echo 'R:', ($result === false), ':', ($right === '0'), ':', ($alias === '0'), ':', ($missing === 9), ';';
$alias = 5;
echo 'A:', ($right === 5), ':', ($result === false), ';END;';
''',
    'peer-reference-right-rebinds-new-string-cell': b'''<?php
function peerRebindRight91($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    $GLOBALS['missing'] = 9;
    $GLOBALS['right'] =& $GLOBALS['target'];
    return true;
}
$right = 0;
$old =& $right;
$target = '0';
set_error_handler('peerRebindRight91');
$result = ($missing < $right);
echo 'R:', ($result === true), ':', ($right === '0'), ':', ($old === 0), ':', ($missing === 9), ';';
$target = 5;
echo 'A:', ($right === 5), ':', ($old === 0), ';END;';
''',
    'peer-both-missing-right-initialized-on-first-warning': b'''<?php
function peerBothMissing91($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $missing'), ':', $line, ';';
    $GLOBALS['missing'] = 9;
    $GLOBALS['right'] = 1;
    return true;
}
set_error_handler('peerBothMissing91');
$result = ($missing == $right);
echo 'R:', ($result === false), ':', ($missing === 9), ':', ($right === 1), ';END;';
''',
}
