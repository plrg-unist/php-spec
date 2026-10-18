"""Quiet multiplication follows the pinned VM's physical operand order."""


def original(left_expr, right_expr, right, expected, evaluations):
    lines = f'''<?php
function h($n, $m, $file, $line) {{
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $n, ":", $line, ";";
    return true;
}}
function lhs() {{
    $GLOBALS['evaluations'] = $GLOBALS['evaluations'] + 1;
    return $GLOBALS['left'];
}}
$tail = 5; $left = 'bad' . $tail; $right = {right};
$pick = true; $calls = 0; $evaluations = 0; $v = 100;
set_error_handler("h");'''.splitlines()
    lines += [''] * (21 - len(lines))
    lines += ['try {', '    $v = (' + left_expr, '        *',
              '        ' + right_expr + ');',
              f'    echo "R:", $v, ":", ($v === {expected}), ":", ($calls === 0), ":", ($evaluations === {evaluations}), ";";',
              '} catch (Throwable $e) {',
              f'    echo "C:", ($e instanceof TypeError), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", ($calls === 0), ":", ($evaluations === {evaluations}), ":", ($left === "bad5"), ":", ($right === {right}), ";";',
              '} finally { echo "F;"; }',
              '$v = 7; echo "A:", ($v === 7), ";END;";']
    assert lines[22].startswith('    $v = (')
    assert lines[24].startswith('        ')
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'quiet-multiply-constant-cv': original("'bad'", '$right', 'false', '0', 0),
    'quiet-multiply-temporary-cv': original('($pick ? $left : "unused")', '$right', 'null', '0', 0),
    'quiet-multiply-return-cv': original('lhs()', '$right', '3', '0', 1),
    'quiet-multiply-float-result': original('2.5', '$right', '4', '10.0', 0),
}
