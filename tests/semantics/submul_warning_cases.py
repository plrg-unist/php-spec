"""SUB/MUL convert the selected LEFT then the already-selected RIGHT cell."""


def original(operator, result, *, first_throw=False, second_throw=False):
    lines = f'''<?php
function h($n, $m, $file, $line) {{
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":", ($m === 'A non-numeric value encountered'), ";";
    if ($GLOBALS['calls'] === 1) {{
        $GLOBALS['left'] = 99; $GLOBALS['right'] = '5tail';
        if ($GLOBALS['throw_first']) {{ throw $GLOBALS['supplied']; }}
        return true;
    }}
    $GLOBALS['left'] = 88; $GLOBALS['right'] = 7;
    if ($GLOBALS['throw_second']) {{ throw $GLOBALS['supplied']; }}
    return true;
}}
$calls = 0; $throw_first = {'true' if first_throw else 'false'}; $throw_second = {'true' if second_throw else 'false'}; $tail = '5';
$left = '12tail'; $leftAlias =& $left; $right = 'bad' . $tail; $rightAlias =& $right; $v = 100;'''.splitlines()
    lines += [''] * (19 - len(lines))
    lines += ['$supplied = new Exception("supplied");', 'set_error_handler("h");', 'try {',
              '    $v = ($left', '        ' + operator, '        $right);',
              f'    echo "R:", $v, ":", ($v === {result}), ":", $left, ":", $leftAlias, ":", $right, ":", $rightAlias, ":", $calls, ";";',
              '} catch (Throwable $e) {',
              '    echo "C:", ($e === $supplied), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $left, ":", $leftAlias, ":", $right, ":", $rightAlias, ":", $calls, ";";',
              '} finally { echo "F;"; }', '$left = 1; $right = 2;',
              'echo "A:", $left, ":", $leftAlias, ":", $right, ":", $rightAlias, ";END;";']
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'submul-sub-cached': original('-', 7),
    'submul-mul-cached': original('*', 60),
    'submul-sub-first-throw': original('-', 7, first_throw=True),
    'submul-mul-second-throw': original('*', 60, second_throw=True),
}
