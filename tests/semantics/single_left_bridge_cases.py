"""An initially quiet integer RHS can change during the LEFT deprecation."""


def original(operator, produced, result, *, level=0, message='', final_right=10, retained=None, throw=False):
    right_check = retained if retained is not None else str(final_right)
    lines = f'''<?php
function h($n, $m, $file, $line) {{
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":";
    if ($GLOBALS['calls'] === 1) {{
        echo ($m === "Implicit conversion from float 12.5 to int loses precision"), ";";
        $GLOBALS['alias'] =& $GLOBALS['left']; $GLOBALS['left'] = 99;
        $GLOBALS['right'] = {produced}; return true;
    }}
    echo (($n === {level}) && ($m === '{message}')), ";";
    $GLOBALS['left'] = 88; $GLOBALS['right'] = {final_right};
    if ($GLOBALS['throw_second']) {{ throw $GLOBALS['second']; }}
    return true;
}}
$calls = 0; $throw_second = {'true' if throw else 'false'}; $tail = '5tail'; $left = 12.5; $right = 3; $v = 100;'''.splitlines()
    assert len(lines) <= 19
    lines += [''] * (19 - len(lines))
    lines += ['$second = new Exception("supplied");', 'set_error_handler("h");', 'try {',
              '    $v = ($left', '        ' + operator + '=', '        $right);',
              f'    echo "R:", $v, ":", ($v === {result}), ":", $left, ":", $alias, ":", $right, ":", ($right === {right_check}), ":", $calls, ";";',
              '} catch (Throwable $e) {',
              '    echo "C:", ($e === $second), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $left, ":", $alias, ":", $right, ":", $calls, ";";',
              '} finally { echo "F;"; }', '$left = 7;', 'echo "A:", $left, ":", $alias, ";END;";']
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'single-left-mod-leading-carrier': original('%', "'0' . $GLOBALS['tail']", 2, level=2, message='A non-numeric value encountered', final_right=7),
    'single-left-shift-quiet-string': original('<<', "'5'", 384, retained="'5'"),
    'single-left-right-float': original('>>', '2.5', 3, level=8192, message='Implicit conversion from float 2.5 to int loses precision', final_right=1),
    'single-left-and-integral': original('&', '5.0', 4, retained='5.0'),
    'single-left-or-bool': original('|', 'true', 13, retained='true'),
    'single-left-xor-precision': original('^', "'5.5'", 9, level=8192, message='Implicit conversion from float-string "5.5" to int loses precision'),
    'single-left-new-warning-throw': original('%', "'0' . $GLOBALS['tail']", 2, level=2, message='A non-numeric value encountered', final_right=7, throw=True),
}
