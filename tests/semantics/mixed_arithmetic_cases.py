"""Mixed plain-variable/reference arithmetic selects referents before diagnostics."""


def original(operator, result, *, left_reference, quiet=False, power=False, throw_at=0):
    left = '12' if quiet else "'0tail'" if power else "'12tail'"
    right = "'5tail'" if quiet else "'bad' . $tail"
    repaired = "'-2tail'" if power else "'5tail'"
    initial_right = "'5tail'" if quiet else "'bad5'"
    selected = 'left' if left_reference else 'right'
    first = f"($GLOBALS['left'] === {left}) && ($GLOBALS['right'] === {initial_right})"
    second = f"($GLOBALS['left'] === 99) && ($GLOBALS['right'] === {repaired})"
    lines = f'''<?php
function h($n, $m, $file, $line) {{
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":", ($m === ($n === 2 ? 'A non-numeric value encountered' : 'Power of base 0 and negative exponent is deprecated')), ":", ($GLOBALS['calls'] === 1 ? ({first}) : ($GLOBALS['calls'] === 2 ? ({second}) : (($GLOBALS['left'] === 88) && ($GLOBALS['right'] === 7)))), ":", ($GLOBALS['selectedAlias'] === $GLOBALS['{selected}']), ";";
    if ($GLOBALS['calls'] === 1) {{ $GLOBALS['left'] = 99; $GLOBALS['right'] = {'7' if quiet else repaired}; }}
    elseif ($GLOBALS['calls'] === 2) {{ $GLOBALS['left'] = 88; $GLOBALS['right'] = 7; }}
    else {{ $GLOBALS['left'] = 77; $GLOBALS['right'] = 9; }}
    if ($GLOBALS['calls'] === $GLOBALS['throwAt']) {{ throw $GLOBALS['supplied']; }}
    return true;
}}
$calls = 0; $throwAt = {throw_at}; $tail = 5;
$left = {left}; $right = {right}; $v = 100;
$selectedAlias =& ${selected};'''.splitlines()
    lines += [''] * (19 - len(lines))
    lines += ['$supplied = new Exception("supplied");', 'set_error_handler("h");', 'try {',
              '    $v = ($left', '        ' + operator, '        $right);',
              f'    echo "R:", $v, ":", ($v === {result}), ":", $left, ":", $right, ":", $selectedAlias, ":", $calls, ";";',
              '} catch (Throwable $e) {',
              '    echo "C:", ($e === $supplied), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $left, ":", $right, ":", $selectedAlias, ":", $calls, ";";',
              '} finally { echo "F;"; }', '$left = 1; $right = 2;',
              'echo "A:", $left, ":", $right, ":", $selectedAlias, ";END;";']
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'mixed-arithmetic-add-right-warning': original('+', '17', left_reference=True, quiet=True),
    'mixed-arithmetic-sub-cached': original('-', '7', left_reference=False),
    'mixed-arithmetic-mul-cached': original('*', '60', left_reference=True),
    'mixed-arithmetic-div-cached': original('/', '2.4', left_reference=False),
    'mixed-arithmetic-power-deprecated': original('**', '1e999', left_reference=True, power=True),
    'mixed-arithmetic-power-deprecated-throw': original('**', '1e999', left_reference=True, power=True, throw_at=3),
}
