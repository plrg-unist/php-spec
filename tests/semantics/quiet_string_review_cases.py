"""Quiet string masks preserve historical LEFT and distinct success/error stores."""

CASES = {
    'quiet-string-negative-xor-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:",
        $GLOBALS['calls'], ":", $n, ":",
        $line, ":";
    if ($GLOBALS['calls'] === 1) {
        echo ($m === "Implicit conversion from float 12.5 to int loses precision"), ";";
        $GLOBALS['alias'] =& $GLOBALS['left'];
        $GLOBALS['left'] = 99;
        $GLOBALS['right'] = '-1';
        return false;
    }
    echo "BAD-H;";
    return true;
}
$calls = 0;
$left = 12.5;
$right = 8.5;
$v = 100;
set_error_handler('h');
try {
    $v = ($left
        ^=
        $right);
    echo "R:", $v, ":", ($v === -13), ":", $left, ":", $alias, ":", ($right === '-1'), ":", $calls, ";";
    $left = 7;
    echo "A:", $left, ":", $alias, ";";
} catch (Throwable $e) {
    echo "BAD-C:", $e->getMessage(), ";";
} finally {
    echo "F;";
}
echo "END;";
''',
    'quiet-string-negative-shift-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:",
        $GLOBALS['calls'], ":", $n, ":",
        $line, ":";
    if ($GLOBALS['calls'] === 1) {
        echo ($m === "Implicit conversion from float 12.5 to int loses precision"), ";";
        $GLOBALS['alias'] =& $GLOBALS['left'];
        $GLOBALS['left'] = 99;
        $GLOBALS['right'] = '-1';
        return false;
    }
    echo "BAD-H;";
    return true;
}
$calls = 0;
$left = 12.5;
$right = 8.5;
$v = 100;
set_error_handler('h');
try {
    $v = ($left
        >>=
        $right);
    echo "BAD-R;";
} catch (Throwable $e) {
    echo "C:", ($e instanceof ArithmeticError), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $left, ":", $alias, ":", ($right === '-1'), ":", $calls, ";";
    $left = 7;
    echo "A:", $left, ":", $alias, ";";
} finally {
    echo "F;";
}
echo "END;";
''',
    'quiet-string-zero-modulo-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:",
        $GLOBALS['calls'], ":", $n, ":",
        $line, ":";
    if ($GLOBALS['calls'] === 1) {
        echo ($m === "Implicit conversion from float 12.5 to int loses precision"), ";";
        $GLOBALS['alias'] =& $GLOBALS['left'];
        $GLOBALS['left'] = 99;
        $GLOBALS['right'] = '0';
        return false;
    }
    echo "BAD-H;";
    return true;
}
$calls = 0;
$left = 12.5;
$right = 8.5;
$v = 100;
set_error_handler('h');
try {
    $v = ($left
        %=
        $right);
    echo "BAD-R;";
} catch (Throwable $e) {
    echo "C:", ($e instanceof DivisionByZeroError), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $left, ":", $alias, ":", ($right === '0'), ":", $calls, ";";
    $left = 7;
    echo "A:", $left, ":", $alias, ";";
} finally {
    echo "F;";
}
echo "END;";
''',
}
