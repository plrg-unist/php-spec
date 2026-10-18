"""A failed delayed RHS uses live type labels and preserves callback stores."""

CASES = {
    'delayed-type-failure-xor-string-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":",
        $n, ":", $line, ":";
    echo ($m ===
        "Implicit conversion from float 12.5 to int loses precision"), ";";
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = 'abc';
    $GLOBALS['right'] = 'xyz';
    return false;
}

$calls = 0;
$left = 12.5;
$right = 8.5;
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
    echo "C:", ($e instanceof TypeError), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", ($left === 'abc'), ":", ($alias === 'abc'), ":", ($right === 'xyz'), ":", $calls, ";";
    $left = 7;
    echo "A:", $left, ":", $alias, ":", ($right === 'xyz'), ";";
} finally {
    echo "F;";
}
echo "END;";
''',
    'delayed-type-failure-mod-array-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":",
        $n, ":", $line, ":";
    echo ($m ===
        "Implicit conversion from float 12.5 to int loses precision"), ";";
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = null;
    $GLOBALS['right'] = [3];
    return false;
}

$calls = 0;
$left = 12.5;
$right = 8.5;
$v = 100;
set_error_handler(
    'h'
);

try {
    $v = ($left
        %=
        $right);
    echo "BAD-R;";
} catch (Throwable $e) {
    echo "C:", ($e instanceof TypeError), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", ($left === null), ":", ($alias === null), ":", ($right[0] === 3), ":", $calls, ";";
    $left = 7;
    echo "A:", $left, ":", $alias, ":", ($right[0] === 3), ";";
} finally {
    echo "F;";
}
echo "END;";
''',
    'delayed-type-failure-shift-array-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":",
        $n, ":", $line, ":";
    echo ($m ===
        "Implicit conversion from float 12.5 to int loses precision"), ";";
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = false;
    $GLOBALS['right'] = [3];
    return false;
}

$calls = 0;
$left = 12.5;
$right = 8.5;
$v = 100;
set_error_handler(
    'h'
);

try {
    $v = ($left
        >>=
        $right);
    echo "BAD-R;";
} catch (Throwable $e) {
    echo "C:", ($e instanceof TypeError), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", ($left === false), ":", ($alias === false), ":", ($right[0] === 3), ":", $calls, ";";
    $left = 7;
    echo "A:", $left, ":", $alias, ":", ($right[0] === 3), ";";
} finally {
    echo "F;";
}
echo "END;";
''',
}
