"""Ordinary integer operators after a fractional LEFT and live object RIGHT."""


RESULTS = {'%': 2, '<<': 384, '>>': 0, '&': 4, '|': 13, '^': 9}


def source(operator, mode='replace'):
    assert operator in RESULTS
    assert mode in ('replace', 'retain', 'throw', 'quiet')
    result = RESULTS[operator]
    lines = [
        '<?php',
        'function h($level, $message, $file, $line) {',
        "    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;",
        "    echo 'H:', $level === E_DEPRECATED, ':', $line === 24, ':', $message === 'Implicit conversion from float 12.5 to int loses precision', ':', $file === __FILE__, ':', $GLOBALS['left'] === 12.5, ':', $GLOBALS['right'] instanceof stdClass, ';';",
        "    $GLOBALS['left'] = 99.5;",
        ("    $GLOBALS['right'] = 5;" if mode in ('replace', 'throw') else "    // Keep the original object for the second conversion."),
        ("    throw $GLOBALS['failure'];" if mode == 'throw' else '    return false;'),
        '}',
        ('$left = 12; $right = new stdClass(); $calls = 0; $v = 100;' if mode == 'quiet' else
         '$left = 12.5; $right = new stdClass(); $calls = 0; $v = 100;'),
    ]
    lines += [''] * (19 - len(lines))
    lines += [
        "$failure = new Exception('integer-object');",
        "set_error_handler('h');",
        'try {',
        '    $v =',
        f'        $left {operator} $right;',
    ]
    if mode == 'replace':
        lines += [
            f"    echo 'R:', $v === {result}, ':', $calls === 1, ':', $left === 99.5, ':', $right === 5, ';';",
            "} catch (Throwable $e) { echo 'BAD-E:', get_class($e), ';';",
        ]
    elif mode == 'throw':
        lines += [
            "    echo 'BAD-R;';",
            '} catch (Throwable $e) {',
            "    echo 'C:', $e === $failure, ':', $e->getLine() === 20, ':', $e->getPrevious() === null, ':', $v === 100, ':', $calls === 1, ':', $left === 99.5, ':', $right === 5, ';';",
        ]
    else:
        lines += [
            "    echo 'BAD-R;';",
            '} catch (TypeError $e) {',
            "    echo 'C:', $e->getLine() === 24, ':', $e->getPrevious() === null, ':', $v === 100, ':', $calls === " + ('0' if mode == 'quiet' else '1') + ", ':', $left === " + ('12' if mode == 'quiet' else '99.5') + ", ':', $right instanceof stdClass, ':', $e->getMessage(), ';';",
        ]
    lines += [
        '}',
        "finally { echo 'F;'; }",
        'restore_error_handler();',
        "echo 'END:', $v === " + ('100' if mode != 'replace' else str(result)) + ", ':', $calls === " + ('0' if mode == 'quiet' else '1') + ";",
    ]
    assert lines[19] == "$failure = new Exception('integer-object');"
    assert lines[23] == f'        $left {operator} $right;'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    **{f'{name}-replace': source(operator) for name, operator in
       (('mod', '%'), ('shl', '<<'), ('shr', '>>'), ('and', '&'), ('or', '|'), ('xor', '^'))},
    'mod-retain-typeerror': source('%', 'retain'),
    'and-retain-typeerror': source('&', 'retain'),
    'shl-handler-throw': source('<<', 'throw'),
    'xor-handler-throw': source('^', 'throw'),
    'and-quiet-typeerror-control': source('&', 'quiet'),
}
