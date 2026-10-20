"""Original two-Warning spaceship sources, frozen independently before implementation."""

CASES = {
    'peer-second-warning-spaceship-fresh-reference': b'''<?php
function peerSecondReference99($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $left'), ':', ($m === 'Undefined variable $right'), ':', $line, ';';
    if ($m === 'Undefined variable $left') {
        $GLOBALS['left'] = 9;
    } else {
        $GLOBALS['alias'] =& $GLOBALS['right'];
        $GLOBALS['right'] = '0';
    }
    return true;
}
$result = 41;
set_error_handler('peerSecondReference99');
$result = ($left
    <=>
    $right);
echo 'R:', ($result === 0), ':', ($left === 9), ':', ($right === '0'), ':', ($alias === '0'), ';';
$alias = 5;
echo 'A:', ($right === 5), ':', ($result === 0), ';END;';
''',
    'peer-second-warning-spaceship-unset-right-target-reference': b'''<?php
function peerSecondTarget99($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $left'), ':', ($m === 'Undefined variable $right'), ':', $line, ';';
    if ($m === 'Undefined variable $left') {
        unset($GLOBALS['right']);
    } else {
        $GLOBALS['right'] =& $GLOBALS['target'];
    }
    return false;
}
$right = 0; $target = '0'; $result = 41;
set_error_handler('peerSecondTarget99');
$result = ($left <=> $right);
echo 'R:', ($result === 0), ':', !isset($left), ':', ($right === '0'), ';';
$target = 5;
echo 'A:', ($right === 5), ':', ($result === 0), ';END;';
''',
    'peer-second-warning-spaceship-same-name': b'''<?php
function peerSecondSame99($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $x'), ':', $line, ':', $GLOBALS['calls'], ';';
    if ($GLOBALS['calls'] === 2) { $GLOBALS['x'] = '0'; }
    return true;
}
$calls = 0; $result = 41;
set_error_handler('peerSecondSame99');
$result = ($x <=> $x);
echo 'R:', ($result === 0), ':', ($x === '0'), ':', ($calls === 2), ';END;';
''',
    'peer-second-warning-spaceship-supplied-throw': b'''<?php
function peerSecondThrow99($n, $m, $file, $line) {
    echo 'H:', ($n === 2), ':', ($m === 'Undefined variable $left'), ':', ($m === 'Undefined variable $right'), ':', $line, ';';
    if ($m === 'Undefined variable $right') { throw $GLOBALS['chosen']; }
    return true;
}
$chosen = new Exception('selected'); $result = 41;
set_error_handler('peerSecondThrow99');
try { $result = ($left <=> $right); echo 'BAD;'; }
catch (Exception $caught) { echo 'C:', ($caught === $chosen), ':', ($result === 41), ':', !isset($left), ':', !isset($right), ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
}
