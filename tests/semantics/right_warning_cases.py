"""Quiet selected LEFT then a leading-number Warning from the selected RHS."""


def original(operator, result, *, thrown=False):
    lines = f'''<?php
function h($n, $m, $file, $line) {{
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":", ($m === 'A non-numeric value encountered'), ":", ($GLOBALS['left'] === 12), ":", ($GLOBALS['right'] === '5tail'), ";";
    $GLOBALS['left'] = 99; $GLOBALS['right'] = 7;
    if ($GLOBALS['throw_warning']) {{ throw $GLOBALS['supplied']; }}
    return true;
}}
$calls = 0; $throw_warning = {'true' if thrown else 'false'};
$left = 12; $leftAlias =& $left; $right = '5tail'; $rightAlias =& $right; $v = 100;'''.splitlines()
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
    'right-warning-add-cached': original('+', '17'),
    'right-warning-sub-cached': original('-', '7'),
    'right-warning-mul-cached': original('*', '60'),
    'right-warning-div-cached': original('/', '2.4'),
    'right-warning-power-cached': original('**', '248832'),
    'right-warning-mul-supplied-throw': original('*', '60', thrown=True),
}
