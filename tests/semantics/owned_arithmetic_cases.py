"""Reference results retain scalar referents through arithmetic diagnostics."""


def original(operator, left_expr, right_expr, initial_left, initial_right, guards,
             actions, result, source_calls, *, throw_at=0):
    phase_guard = f"($GLOBALS['calls'] === 1 ? ({guards[0]}) : ($GLOBALS['calls'] === 2 ? ({guards[1]}) : ({guards[2]})))"
    lines = f'''<?php
function h($n, $m, $file, $line) {{
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":", ($m === ($n === 2 ? 'A non-numeric value encountered' : 'Power of base 0 and negative exponent is deprecated')), ":", {phase_guard}, ":", ($GLOBALS['sourceCalls'] === {source_calls}), ";";
    if ($GLOBALS['calls'] === 1) {{ {actions[0]} }}
    elseif ($GLOBALS['calls'] === 2) {{ {actions[1]} }}
    else {{ {actions[2]} }}
    if ($GLOBALS['calls'] === $GLOBALS['throwAt']) {{ throw $GLOBALS['supplied']; }}
    return true;
}}
function &lhs() {{ $GLOBALS['sourceCalls'] = $GLOBALS['sourceCalls'] + 1; return $GLOBALS['left']; }}
function &rhs() {{ $GLOBALS['sourceCalls'] = $GLOBALS['sourceCalls'] + 1; return $GLOBALS['right']; }}
$calls = 0; $sourceCalls = 0; $throwAt = {throw_at}; $tail = 5;
$left = {initial_left}; $right = {initial_right}; $alias = 0; $v = 100;'''.splitlines()
    lines += [''] * (19 - len(lines))
    lines += ['$supplied = new Exception("supplied");', 'set_error_handler("h");', 'try {',
              '    $v = (' + left_expr, '        ' + operator, '        ' + right_expr + ');',
              f'    echo "R:", $v, ":", ($v === {result}), ":", $calls, ":", $sourceCalls, ":", !isset($alias), ":", !isset($left), ":", !isset($right), ";";',
              '} catch (Throwable $e) {',
              '    echo "C:", ($e === $supplied), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", (isset($left) && $left === 77), ":", (isset($right) && $right === 9), ":", $calls, ":", $sourceCalls, ";";',
              '} finally { echo "F;"; }', '$left = 1; $right = 2; $alias = 3;',
              'echo "A:", $left, ":", $right, ":", $alias, ";END;";']
    return ('\n'.join(lines) + '\n').encode()


MISSING = "!isset($GLOBALS['left']) && !isset($GLOBALS['right']) && !isset($GLOBALS['alias'])"
POWER_GUARDS = ("$GLOBALS['left'] === '0tail' && $GLOBALS['right'] === 'bad5'",
                "!isset($GLOBALS['left']) && !isset($GLOBALS['right'])",
                "$GLOBALS['left'] === 88 && $GLOBALS['right'] === 7")
POWER_ACTIONS = ("$GLOBALS['left'] = 99; $GLOBALS['right'] = '-2tail'; unset($GLOBALS['left'], $GLOBALS['right']);",
                 "$GLOBALS['left'] = 88; $GLOBALS['right'] = 7;",
                 "$GLOBALS['left'] = 77; $GLOBALS['right'] = 9;")
CASES = {
    'owned-arithmetic-add-right-refassign': original('+', '$left', '($alias =& $right)', '12', "'5tail'",
        ("$GLOBALS['left'] === 12 && $GLOBALS['right'] === '5tail' && $GLOBALS['alias'] === '5tail'", 'false', 'false'),
        ("$GLOBALS['left'] = 99; $GLOBALS['right'] = 7; unset($GLOBALS['right'], $GLOBALS['alias']);", '', ''), '17', 0),
    'owned-arithmetic-sub-left-refcall': original('-', 'lhs()', '$right', "'12tail'", "'bad' . $tail",
        ("$GLOBALS['left'] === '12tail' && $GLOBALS['right'] === 'bad5'", "!isset($GLOBALS['left']) && $GLOBALS['right'] === '5tail'", 'false'),
        ("$GLOBALS['left'] = 99; $GLOBALS['right'] = '5tail'; unset($GLOBALS['left']);", "unset($GLOBALS['right']);", ''), '7', 1),
    'owned-arithmetic-mul-swapped-refassign': original('*', '($alias =& $left)', '$right', "'bad' . $tail", "'5tail'",
        ("$GLOBALS['left'] === 'bad5' && $GLOBALS['right'] === '5tail' && $GLOBALS['alias'] === 'bad5'", "!isset($GLOBALS['left']) && !isset($GLOBALS['alias']) && $GLOBALS['right'] === 7", 'false'),
        ("$GLOBALS['left'] = '12tail'; $GLOBALS['right'] = 7; unset($GLOBALS['left'], $GLOBALS['alias']);", "$GLOBALS['right'] = 8;", ''), '60', 0),
    'owned-arithmetic-div-both-unset': original('/', 'lhs()', '($alias =& $right)', "'12tail'", "'bad' . $tail",
        ("$GLOBALS['left'] === '12tail' && $GLOBALS['right'] === 'bad5' && $GLOBALS['alias'] === 'bad5'", MISSING, 'false'),
        ("$GLOBALS['left'] = 99; $GLOBALS['right'] = '5tail'; unset($GLOBALS['left'], $GLOBALS['right'], $GLOBALS['alias']);", "$GLOBALS['left'] = 88; $GLOBALS['right'] = 7;", ''), '2.4', 1),
    'owned-arithmetic-power-deprecated': original('**', 'lhs()', 'rhs()', "'0tail'", "'bad' . $tail", POWER_GUARDS, POWER_ACTIONS, '1e999', 2),
    'owned-arithmetic-power-deprecated-throw': original('**', 'lhs()', 'rhs()', "'0tail'", "'bad' . $tail", POWER_GUARDS, POWER_ACTIONS, '1e999', 2, throw_at=3),
}
