"""Copied arithmetic operands freeze before numeric conversion callbacks."""


def original(operator, left_expr, right_expr, initial_left, initial_right, first_right,
             second_right, result, *, throw_at=0, by_value=False, type_failure=False):
    initial_right_value = "'bad5'" if initial_right == "'bad' . $tail" else initial_right
    first = f"($GLOBALS['left'] === {initial_left}) && ($GLOBALS['right'] === {initial_right_value})"
    second = f"($GLOBALS['left'] === 99) && ($GLOBALS['right'] === {first_right})"
    lines = f'''<?php
function h($n, $m, $file, $line) {{
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":", ($m === ($n === 2 ? 'A non-numeric value encountered' : 'Power of base 0 and negative exponent is deprecated')), ":", ($GLOBALS['calls'] === 1 ? ({first}) : ($GLOBALS['calls'] === 2 ? ({second}) : (($GLOBALS['left'] === 88) && ($GLOBALS['right'] === {second_right})))), ":", ($GLOBALS['sourceCalls'] === {1 if by_value else 0}), ";";
    if ($GLOBALS['calls'] === 1) {{ $GLOBALS['left'] = 99; $GLOBALS['right'] = {first_right}; }}
    elseif ($GLOBALS['calls'] === 2) {{ $GLOBALS['left'] = 88; $GLOBALS['right'] = {second_right}; }}
    else {{ $GLOBALS['left'] = 77; $GLOBALS['right'] = 9; }}
    if ($GLOBALS['calls'] === $GLOBALS['throwAt']) {{ throw $GLOBALS['supplied']; }}
    return true;
}}
function lhs() {{ $GLOBALS['sourceCalls'] = $GLOBALS['sourceCalls'] + 1; return $GLOBALS['left']; }}
$calls = 0; $sourceCalls = 0; $choose = true; $throwAt = {throw_at}; $tail = 5;
$left = {initial_left}; $right = {initial_right}; $v = 100;'''.splitlines()
    lines += [''] * (19 - len(lines))
    caught = ('    echo "E:", ($e instanceof TypeError), ":", ($e->getMessage() === "Unsupported operand types: bool * string"), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", ($right === false), ":", $calls, ";";'
              if type_failure else
              '    echo "C:", ($e === $supplied), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $left, ":", $right, ":", $calls, ";";')
    lines += ['$supplied = new Exception("supplied");', 'set_error_handler("h");', 'try {',
              '    $v = (' + left_expr, '        ' + operator, '        ' + right_expr + ');',
              f'    echo "R:", $v, ":", ($v === {result}), ":", $left, ":", $right, ":", $calls, ":", $sourceCalls, ";";',
              '} catch (Throwable $e) {', caught,
              '} finally { echo "F;"; }', '$left = 1; $right = 2;',
              'echo "A:", $left, ":", $right, ";END;";']
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'copied-arithmetic-add-unary-right-warning': original('+', '(+$left)', '$right', '12', "'5tail'", '7', '8', '17'),
    'copied-arithmetic-sub-literal-repair': original('-', "'12tail'", '$right', "'12tail'", "'bad' . $tail", "'5tail'", '7', '7'),
    'copied-arithmetic-mul-swapped': original('*', "'12tail'", '$right', "'12tail'", "'5tail'", '7', '8', '60'),
    'copied-arithmetic-div-return-ternary': original('/', 'lhs()', '($choose ? $right : 0)', "'12tail'", "'5tail'", '7', '8', '2.4', by_value=True),
    'copied-arithmetic-power-deprecated': original('**', '($choose ? $left : 1)', '$right', "'0tail'", "'bad' . $tail", "'-2tail'", '7', '1e999'),
    'copied-arithmetic-mul-swapped-types': original('*', "'bad'", '$right', "'bad'", "'5tail'", 'false', '8', '0', type_failure=True),
    'copied-arithmetic-power-deprecated-throw': original('**', '($choose ? $left : 1)', '$right', "'0tail'", "'bad' . $tail", "'-2tail'", '7', '1e999', throw_at=3),
}
