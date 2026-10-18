"""Selected-reference power conversion warnings followed by safe_pow diagnostics."""


def original(*, zero=False, throw_phase=0):
    lines = f'''<?php
function h($n, $m, $file, $line) {{
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $last = ($GLOBALS['calls'] === 3);
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":", ($m === ($last ? 'Power of base 0 and negative exponent is deprecated' : 'A non-numeric value encountered')), ":", ($n === ($last ? 8192 : 2)), ";";
    if ($GLOBALS['calls'] === 1) {{ $GLOBALS['left'] = 99; $GLOBALS['right'] = '{'-2tail' if zero else '3tail'}'; }}
    elseif ($GLOBALS['calls'] === 2) {{ $GLOBALS['left'] = 88; $GLOBALS['right'] = 7; }}
    else {{ $GLOBALS['left'] = 77; $GLOBALS['right'] = 9; }}
    if ($GLOBALS['calls'] === $GLOBALS['throw_phase']) {{ throw $GLOBALS['supplied']; }}
    return true;
}}
$calls = 0; $throw_phase = {throw_phase}; $tail = '5';
$left = '{'0tail' if zero else '2tail'}'; $leftAlias =& $left; $right = 'bad' . $tail; $rightAlias =& $right; $v = 100;'''.splitlines()
    lines += [''] * (19 - len(lines))
    lines += ['$supplied = new Exception("supplied");', 'set_error_handler("h");', 'try {',
              '    $v = ($left', '        **', '        $right);',
              f'    echo "R:", $v, ":", ($v === {"1e999" if zero else "8"}), ":", $left, ":", $leftAlias, ":", $right, ":", $rightAlias, ":", $calls, ";";',
              '} catch (Throwable $e) {',
              '    echo "C:", ($e === $supplied), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $left, ":", $leftAlias, ":", $right, ":", $rightAlias, ":", $calls, ";";',
              '} finally { echo "F;"; }', '$left = 1; $right = 2;',
              'echo "A:", $left, ":", $leftAlias, ":", $right, ":", $rightAlias, ";END;";']
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'power-conversion-cached-integer': original(),
    'power-conversion-final-deprecated': original(zero=True),
    'power-conversion-second-warning-throw': original(throw_phase=2),
    'power-conversion-final-deprecated-throw': original(zero=True, throw_phase=3),
}
