"""Quiet float counts preserve negative-count errors and the captured LEFT sign."""

HEAD = b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:",
        $GLOBALS['calls'], ":", $n, ":",
        $line, ":";
    if ($GLOBALS['calls'] === 1) {
        echo ($m === "Implicit conversion from float -12.5 to int loses precision"), ";";
        $GLOBALS['alias'] =& $GLOBALS['left'];
        $GLOBALS['left'] = 99;
        $GLOBALS['right'] = -1.0;
        return false;
    }
    echo "BAD-H;";
    return true;
}
$calls = 0;
$left = -12.5;
$right = 8.5;
$v = 100;
set_error_handler('h');
try {
    $v = ($left
        >>=
        $right);
'''

NEGATIVE = HEAD + b'''    echo "BAD-R;";
} catch (Throwable $e) {
    echo "C:", ($e instanceof ArithmeticError), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $left, ":", $alias, ":", ($right === -1.0), ":", $calls, ";";
    $left = 7;
    echo "A:", $left, ":", $alias, ";";
} finally {
    echo "F;";
}
echo "END;";
'''

WIDE = HEAD.replace(b"$GLOBALS['right'] = -1.0;", b"$GLOBALS['right'] = 64.0;") + b'''    echo "R:", $v, ":", ($v === -1), ":", $left, ":", $alias, ":", ($right === 64.0), ":", $calls, ";";
    $left = 7;
    echo "A:", $left, ":", $alias, ";";
} catch (Throwable $e) {
    echo "BAD-C:", $e->getMessage(), ";";
} finally {
    echo "F;";
}
echo "END;";
'''

CASES = {
    'shiftassign-quiet-float-negative-default': NEGATIVE,
    'shiftassign-quiet-float-wide-default': WIDE,
}
