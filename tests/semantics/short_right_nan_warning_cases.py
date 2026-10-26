"""Selected RIGHT NaN truth callbacks in all four short-circuit forms."""


def source(operator, left, selected, throwing=False):
    assert operator in ('&&', 'and', '||', 'or')
    assert selected == (left if operator in ('&&', 'and') else not left)
    change = '1.0' if throwing or operator in ('||', 'or') else '0.0'
    expected = 'true' if operator in ('||', 'or') and selected or not selected and left else 'false'
    lines = [
        '<?php',
        'function left($value) {',
        "    $GLOBALS['left_calls'] = $GLOBALS['left_calls'] + 1;",
        "    echo 'L;';",
        '    return $value;',
        '}',
        'function h($level, $message, $file, $line) {',
        "    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;",
        "    echo 'H:', $level, ':', $line, ':', $message, ':', $file === __FILE__, ';';",
        "    $GLOBALS['x'] = " + change + ';',
        "    " + ("throw $GLOBALS['second'];" if throwing else 'return false;'),
        '}',
        '$x = NAN; $calls = 0; $left_calls = 0; $v = 100;',
    ]
    lines += [''] * (19 - len(lines))
    lines += [
        "$second = new Exception('right-nan');",
        "set_error_handler('h', E_WARNING);",
        'try {',
        '    $v = (',
        '        left(' + ('true' if left else 'false') + ') ' + operator,
        '        $x);',
    ]
    if throwing:
        lines += [
            "    echo 'BAD-R;';",
            '} catch (Throwable $e) {',
            "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', $x === 1.0, ':', $calls === 1, ':', $left_calls === 1, ';';",
        ]
    else:
        x_observer = ", ':', $x === " + change if selected else ''
        lines += [
            "    echo 'R:', $v === " + expected + ", ':', $calls === " + ('1' if selected else '0') + ", ':', $left_calls === 1" + x_observer + ", ';';",
            "} catch (Throwable $e) { echo 'BAD-E;'; }",
        ]
    if throwing:
        lines += ['}']
    lines += [
        "finally { echo 'F;'; }",
        'restore_error_handler();',
        '$x = 8;',
        "echo 'END:', $x === 8, ':', $v === " + ('100' if throwing else expected) + ", ':', $calls === " + ('1' if selected else '0') + ", ':', $left_calls === 1, ';';",
    ]
    assert lines[19] == "$second = new Exception('right-nan');"
    assert lines[24] == '        $x);'
    assert lines[23].endswith(' ' + operator)
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'right-nan-symbolic-and-normal': source('&&', True, True),
    'right-nan-keyword-and-normal': source('and', True, True),
    'right-nan-symbolic-or-normal': source('||', False, True),
    'right-nan-keyword-or-normal': source('or', False, True),
    'right-nan-symbolic-and-throw': source('&&', True, True, True),
    'right-nan-keyword-or-throw': source('or', False, True, True),
    'right-nan-symbolic-and-skip': source('&&', False, False),
    'right-nan-keyword-or-skip': source('or', True, False),
}
