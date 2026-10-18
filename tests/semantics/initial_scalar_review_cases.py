"""RHS conversion waits until after the first fractional-LEFT callback."""

CASES = {
    'initial-scalar-bad-xor-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":",
        $n, ":", $line, ":";
    echo ($m ===
        "Implicit conversion from float 12.5 to int loses precision"), ";";
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = 'abc';
    return false;
}

$calls = 0;
$tail = '5';
$left = 12.5;
$right = 'bad' . $tail;
$v = 100;
set_error_handler(
    'h'
);

try {
    $v = ($left
        ^=
        $right);
    echo "BAD-R;";
} catch (Throwable $e) {
    echo "C:", ($e instanceof TypeError), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", ($left === 'abc'), ":", ($alias === 'abc'), ":", ($right === 'bad5'), ":", $calls, ";";
    $left = 7;
    echo "A:", $left, ":", $alias, ":", ($right === 'bad5'), ";";
} finally {
    echo "F;";
}
echo "END;";
''',
    'initial-scalar-null-negative-reference-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":";
    if ($GLOBALS['calls'] === 1) {
        echo ($m === "Implicit conversion from float 12.5 to int loses precision"), ";";
        $GLOBALS['alias'] =& $GLOBALS['left'];
        $GLOBALS['left'] = 99;
        $GLOBALS['right'] = -1.5;
        return true;
    }
    echo ($m === "Implicit conversion from float -1.5 to int loses precision"), ";";
    $GLOBALS['left'] = 88;
    $GLOBALS['right'] =& $GLOBALS['left'];
    return false;
}
$calls = 0;
$left = 12.5;
$right = null;
$v = 100;
set_error_handler('h');
try {
    $v = ($left
        ^=
        $right);
    echo "R:", $v, ":", ($v === -13), ":", $left, ":", $alias, ":", $right, ":", $calls, ";";
    $left = 7;
    $alias = 6;
    echo "A:", $left, ":", $alias, ":", $right, ";";
} catch (Throwable $e) {
    echo "BAD-C:", $e->getMessage(), ";";
} finally {
    echo "F;";
}
echo "END;";
''',
    'initial-scalar-bad-first-throw': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":",
        $n, ":", $line, ":";
    echo ($m ===
        "Implicit conversion from float 12.5 to int loses precision"), ";";
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = 99;
    throw $GLOBALS['first'];
}
$calls = 0;
$tail = '5';
$left = 12.5;
$right = 'bad' . $tail;
$v = 100;



$first = new Exception("supplied");
set_error_handler('h');
try {
    $v = ($left
        ^=
        $right);
    echo "BAD-R;";
} catch (Throwable $e) {
    echo "C:", ($e === $first), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $left, ":", $alias, ":", ($right === 'bad5'), ":", $calls, ";";
    $left = 7;
    echo "A:", $left, ":", $alias, ":", ($right === 'bad5'), ";";
} finally {
    echo "F;";
}
echo "END;";
''',
}
