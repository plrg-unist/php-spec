"""Failed live RHS conversion after an initially both-fractional compound."""


def original(operator, left, right, left_check, right_check):
    return f'''<?php
function h($n, $m, $file, $line) {{
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":";
    if ($GLOBALS['calls'] === 1) {{
        echo ($m === "Implicit conversion from float 12.5 to int loses precision"), ";";
        $GLOBALS['alias'] =& $GLOBALS['left'];
        $GLOBALS['left'] = {left};
        $GLOBALS['right'] = {right};
        if ($GLOBALS['throw_at'] === 1) {{ throw $GLOBALS['second']; }}
        return true;
    }}
    echo "BAD-H;"; return true;
}}
$calls = 0;
$throw_at = 0; $tail = 5;
$left = 12.5;
$right = 8.5;
$v = 100;
$second = new Exception("supplied");
set_error_handler("h");
try {{
    $v = ($left
        {operator}=
        $right);
    echo "BAD-R:", $v, ";";
}} catch (Throwable $e) {{
    echo "C:", ($e instanceof TypeError), ":", ($e === $second), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", ({left_check}), ":", ({right_check}), ":", $calls, ";";
    $left = 7;
    echo "A:", $left, ":", $alias, ";";
}} finally {{ echo "F;"; }}
echo "END;";
'''.encode()


MOD = original('%', 'true', "'bad' . $GLOBALS['tail']", '$left === true && $alias === true', '$right === "bad5"')
CASES = {
    'delayed-failure-mod-carrier': MOD,
    'delayed-failure-left-null': original('<<', 'null', '"xyz"', '$left === null && $alias === null', '$right === "xyz"'),
    'delayed-failure-right-float': original('>>', '2.0', '"xyz"', '$left === 2.0 && $alias === 2.0', '$right === "xyz"'),
    'delayed-failure-and-strings': original('&', '"abc"', '"xyz"', '$left === "abc" && $alias === "abc"', '$right === "xyz"'),
    'delayed-failure-or-strings': original('|', '"abc"', '"xyz"', '$left === "abc" && $alias === "abc"', '$right === "xyz"'),
    'delayed-failure-xor-strings': original('^', '"abc"', '"xyz"', '$left === "abc" && $alias === "abc"', '$right === "xyz"'),
    'delayed-failure-first-throw': MOD.replace(b'$throw_at = 0;', b'$throw_at = 1;'),
}
