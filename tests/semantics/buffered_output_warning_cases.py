"""OP103: a Warning callback starts a default buffer before cached output."""


def source(kind, throwing=False):
    assert kind in ('print-array', 'echo-array', 'print-nan')
    assert not throwing or kind != 'print-nan'
    initial = 'NAN' if kind == 'print-nan' else '[11, $seed + 22]'
    lines = [
        '<?php',
        'function h($level, $message, $file, $line) {',
        "    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;",
        "    echo 'H:', $level, ':', $line, ':', $message, ':', $file === __FILE__, ';';",
        '    ob_start();',
        "    echo 'I;';",
        "    $GLOBALS['a'] = 99;",
        "    unset($GLOBALS['a']);",
        "    if ($GLOBALS['throw']) throw $GLOBALS['second'];",
        '    return false;',
        '}',
        'function later() {',
        "    $GLOBALS['later_calls'] = $GLOBALS['later_calls'] + 1;",
        "    $GLOBALS['seen'] = ob_get_contents() === 'I;Array|';",
        "    echo 'L;';",
        "    return 'Z';",
        '}',
        f'$seed = 0; $a = {initial}; $calls = 0; $later_calls = 0; $seen = false; $v = 100;',
        '$throw = ' + ('true' if throwing else 'false') + ';',
        "$second = new Exception('buffered-output-warning');",
        "set_error_handler('h', E_WARNING);",
        'try {',
    ]
    if kind == 'echo-array':
        lines += ['    echo', '        $a,', "        '|',", '        later();']
    else:
        lines += ['    $v = (print', '        $a);']
    buffered = 'I;NAN' if kind == 'print-nan' else ('I;Array|L;Z' if kind == 'echo-array' and not throwing else 'I;Array')
    if throwing:
        lines += [
            "    echo 'BAD-R;';",
            '} catch (Throwable $e) {',
            '    $captured = ob_get_clean();',
            "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $captured === '" + buffered + "', ':', $v === 100, ':', !isset($a), ':', $calls === 1, ':', $later_calls === 0, ':', !$seen, ';';",
            '}',
        ]
    else:
        lines += [
            '    $captured = ob_get_clean();',
            "    echo 'R:', $captured === '" + buffered + "', ':', $v === " + ('100' if kind == 'echo-array' else '1') + ", ':', !isset($a), ':', $calls === 1, ':', $later_calls === " + ('1' if kind == 'echo-array' else '0') + ", ':', $seen === " + ('true' if kind == 'echo-array' else 'false') + ", ';';",
            "} catch (Throwable $e) { $captured = ob_get_clean(); echo 'BAD-E;'; }",
        ]
    lines += [
        "finally { echo 'F;'; }",
        'restore_error_handler();',
        '$a = 8;',
        "echo 'END:', $a === 8, ':', $calls === 1, ':', $later_calls === " + ('1' if kind == 'echo-array' and not throwing else '0') + ", ':', ob_get_level() === 0, ';';",
    ]
    assert lines[19] == "$second = new Exception('buffered-output-warning');"
    assert lines[23] == '        $a,' if kind == 'echo-array' else lines[23] == '        $a);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'print-array-buffer-false-default': source('print-array'),
    'print-array-buffer-pending-throw': source('print-array', True),
    'echo-array-buffer-false-default': source('echo-array'),
    'echo-array-buffer-pending-throw': source('echo-array', True),
    'print-nan-buffer-false-default': source('print-nan'),
}
