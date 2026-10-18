"""Quiet MUL rank controls and a saved TMP surviving source repair."""


def original(left_expr, right_expr, right_value, message, *, repaired=False):
    source_calls = 1 if repaired else 0
    left_observer = '$left === 12' if repaired else "$left === 'bad5'"
    lines = f'''<?php
function rhs() {{ $GLOBALS['sourceCalls'] = $GLOBALS['sourceCalls'] + 1; $GLOBALS['left'] = 12; return $GLOBALS['right']; }}
function h($n, $m, $file, $line) {{ $GLOBALS['calls'] = $GLOBALS['calls'] + 1; echo 'BAD-H;'; return false; }}
$calls = 0; $sourceCalls = 0; $tail = 5; set_error_handler('h');
$left = 'bad' . $tail; $right = {right_value}; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ['try {', '    $v =', '        ' + left_expr, '        *', '        ' + right_expr + ';',
              "    echo 'BAD-R;';", '} catch (Throwable $e) {',
              f"    echo 'E:', $e instanceof TypeError, ':', $e->getMessage() === '{message}', ':', $e->getLine(), ':', $e->getPrevious() === null, ':', $v === 100, ':', $calls === 0, ':', $sourceCalls === {source_calls}, ':', {left_observer}, ':', $right === {right_value}, ';';",
              "} finally { echo 'F;'; }", '$left = 7; $right = 8;',
              "echo 'A:', $left === 7, ':', $right === 8, ';END;';"]
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'quiet-multiply-cv-const': original('$left', 'true', 'false',
        'Unsupported operand types: string * bool'),
    'quiet-multiply-equal-tmp': original('(true ? $left : 0)', '(true ? $right : 0)', 'false',
        'Unsupported operand types: string * bool'),
    'quiet-multiply-tmp-var-copy': original('(true ? $left : 0)', 'rhs()', '2.5',
        'Unsupported operand types: float * string', repaired=True),
}
