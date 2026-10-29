"""Ordinary binary bitwise conversion of a computed LEFT temporary."""


def source(operator, throwing=False, quiet=False, arithmetic='+'):
    assert operator in ('&', '|', '^')
    assert arithmetic in ('+', '*', '/')
    assert not (throwing and quiet)
    result = {'&': 4, '|': 13, '^': 9}[operator]
    quiet_result = {'&': 4, '|': 13, '^': 9}[operator]
    lines = [
        '<?php',
        'function h($level, $message, $file, $line) {',
        "    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;",
        "    echo 'H:', $GLOBALS['calls'], ':', $level, ':', $line, ':', $message, ':', $file === __FILE__, ';';",
        "    if ($GLOBALS['calls'] === 1) {",
        "        $GLOBALS['left'] = 99;",
        "        $GLOBALS['right'] = 2.5;",
        '    } else {',
        "        $GLOBALS['right'] = 88;",
        ("        throw $GLOBALS['failure'];" if throwing else "        return false;"),
        '    }',
        '    return false;',
        '}',
        ('$left = 12; $right = 5; $calls = 0; $v = 100;' if quiet else
         '$left = 12.5; $right = 5.5; $calls = 0; $v = 100;'),
    ]
    lines += [''] * (19 - len(lines))
    lines += [
        "$failure = new Exception('bitwise-tmp');",
        "set_error_handler('h');",
        'try {',
        '    $v =',
        '        ($left ' + arithmetic + (' 1.0' if arithmetic in ('*', '/') else ' 0.0') + ') ' + operator + ' $right;',
    ]
    if throwing:
        lines += [
            "    echo 'BAD-R;';",
            '} catch (Throwable $e) {',
            "    echo 'C:', $e === $failure, ':', $e->getLine() === 20, ':', $v === 100, ':', $calls === 2, ':', $left === 99, ':', $right === 88, ';';",
        ]
    elif quiet:
        lines += [
            f"    echo 'Q:', $v === {quiet_result}, ':', $calls === 0, ':', $left === 12, ':', $right === 5, ';';",
            "} catch (Throwable $e) { echo 'BAD-E;';",
        ]
    else:
        lines += [
            f"    echo 'R:', $v === {result}, ':', $calls === 2, ':', $left === 99, ':', $right === 88, ';';",
            "} catch (Throwable $e) { echo 'BAD-E;';",
        ]
    lines += [
        '}',
        "finally { echo 'F;'; }",
        'restore_error_handler();',
        "echo 'END:', $v === " + ('100' if throwing else str(quiet_result if quiet else result)) + ", ':', $calls === " + ('0' if quiet else '2') + ";",
    ]
    assert lines[19] == "$failure = new Exception('bitwise-tmp');"
    assert lines[23] == '        ($left ' + arithmetic + (' 1.0' if arithmetic in ('*', '/') else ' 0.0') + ') ' + operator + ' $right;'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    **{f'computed-left-{name}-default': source(operator)
       for name, operator in (('and', '&'), ('or', '|'), ('xor', '^'))},
    **{f'computed-left-{name}-second-throw': source(operator, throwing=True)
       for name, operator in (('and', '&'), ('or', '|'), ('xor', '^'))},
    'computed-left-mul-or-default': source('|', arithmetic='*'),
    'computed-left-div-xor-default': source('^', arithmetic='/'),
    'computed-left-and-quiet-control': source('&', quiet=True),
}
