"""LEFT converts before an initially noninteger scalar RHS is examined."""


def original(operator, initial, produced, result, *, initial_check=None, level=0, message='', final_right=10, retained=None):
    right_check = retained if retained is not None else str(final_right)
    initial_check = initial_check or initial
    lines = f'''<?php
function h($n, $m, $file, $line) {{
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":";
    if ($GLOBALS['calls'] === 1) {{
        echo (($m === "Implicit conversion from float 12.5 to int loses precision") && ($GLOBALS['right'] === {initial_check})), ";";
        $GLOBALS['alias'] =& $GLOBALS['left']; $GLOBALS['left'] = 99;
        $GLOBALS['right'] = {produced}; return true;
    }}
    echo (($n === {level}) && ($m === '{message}')), ";";
    $GLOBALS['left'] = 88; $GLOBALS['right'] = {final_right};
    return true;
}}
$calls = 0; $tail = '5'; $left = 12.5; $right = {initial}; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ['set_error_handler("h");', 'try {',
              '    $v = ($left', '        ' + operator + '=', '        $right);',
              f'    echo "R:", $v, ":", ($v === {result}), ":", $left, ":", $alias, ":", $right, ":", ($right === {right_check}), ":", $calls, ";";',
              '} catch (Throwable $e) { echo "BAD-C:", $e->getMessage(), ";";',
              '} finally { echo "F;"; }', '$left = 7;', 'echo "A:", $left, ":", $alias, ";END;";']
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'initial-scalar-mod-repaired-carrier': original('%', "'bad' . $tail", '5.5', 2, initial_check="'bad5'", level=8192, message='Implicit conversion from float 5.5 to int loses precision', final_right=7),
    'initial-scalar-shift-null-entry': original('<<', 'null', "'5'", 384, retained="'5'"),
    'initial-scalar-right-bool-entry': original('>>', 'false', '2.5', 3, level=8192, message='Implicit conversion from float 2.5 to int loses precision', final_right=1),
    'initial-scalar-and-integral-entry': original('&', '10.0', '5.0', 4, retained='5.0'),
    'initial-scalar-or-text-entry': original('|', "'2'", 'true', 13, retained='true'),
    'initial-scalar-xor-leading-entry': original('^', "'7tail'", "'5.5'", 9, level=8192, message='Implicit conversion from float-string "5.5" to int loses precision'),
}
