"""Initially plain arithmetic CVs retain numbers across conversion diagnostics."""


def original(operator, result, *, quiet=False, power=False, throw_at=0):
    left = '12' if quiet else "'0tail'" if power else "'12tail'"
    right = "'5tail'" if quiet else "'bad' . $tail"
    repaired = "'-2tail'" if power else "'5tail'"
    initial_right = "'5tail'" if quiet else "'bad5'"
    first = f"($GLOBALS['left'] === {left}) && ($GLOBALS['right'] === {initial_right})"
    second = f"($GLOBALS['left'] === 99) && ($GLOBALS['right'] === {repaired})"
    lines = f'''<?php
function h($n, $m, $file, $line) {{
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":", ($m === ($n === 2 ? 'A non-numeric value encountered' : 'Power of base 0 and negative exponent is deprecated')), ":", ($GLOBALS['calls'] === 1 ? ({first}) : ($GLOBALS['calls'] === 2 ? ({second}) : (($GLOBALS['left'] === 88) && ($GLOBALS['right'] === 7)))), ";";
    if ($GLOBALS['calls'] === 1) {{ $GLOBALS['left'] = 99; $GLOBALS['right'] = {'7' if quiet else repaired}; }}
    elseif ($GLOBALS['calls'] === 2) {{ $GLOBALS['left'] = 88; $GLOBALS['right'] = 7; }}
    else {{ $GLOBALS['left'] = 77; $GLOBALS['right'] = 9; }}
    if ($GLOBALS['calls'] === $GLOBALS['throwAt']) {{ throw $GLOBALS['supplied']; }}
    return true;
}}
$calls = 0; $throwAt = {throw_at}; $tail = 5;
$left = {left}; $right = {right}; $v = 100;'''.splitlines()
    lines += [''] * (19 - len(lines))
    lines += ['$supplied = new Exception("supplied");', 'set_error_handler("h");', 'try {',
              '    $v = ($left', '        ' + operator, '        $right);',
              f'    echo "R:", $v, ":", ($v === {result}), ":", $left, ":", $right, ":", $calls, ";";',
              '} catch (Throwable $e) {',
              '    echo "C:", ($e === $supplied), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $left, ":", $right, ":", $calls, ";";',
              '} finally { echo "F;"; }', '$left = 1; $right = 2;',
              'echo "A:", $left, ":", $right, ";END;";']
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'plain-arithmetic-add-right-warning': original('+', '17', quiet=True),
    'plain-arithmetic-sub-cached': original('-', '7'),
    'plain-arithmetic-mul-cached': original('*', '60'),
    'plain-arithmetic-div-cached': original('/', '2.4'),
    'plain-arithmetic-power-deprecated': original('**', '1e999', power=True),
    'plain-arithmetic-right-warning-throw': original('*', '60', throw_at=2),
    'plain-arithmetic-power-deprecated-throw': original('**', '1e999', power=True, throw_at=3),
}
