"""OP98 originals: acquired by-value array result in used print Warning."""


def source(throwing=False, scalar=False):
    result = '7' if scalar else "$GLOBALS['a']"
    lines = [
        '<?php',
        'function print_array_handler($level, $message, $file, $line) {',
        "    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;",
        "    echo 'H:', $level, ':', $line, ':', $message, ':', $file === __FILE__, ';';",
        "    unset($GLOBALS['a']);",
        "    $GLOBALS['seed'] = 99;",
        "    if ($GLOBALS['throw']) throw $GLOBALS['second'];",
        '    return false;',
        '}',
        'function take() {',
        "    $GLOBALS['made'] = $GLOBALS['made'] + 1;",
        "    echo 'P;';",
        f'    return {result};',
        '}',
        '$seed = 0; $a = [11, $seed + 22]; $made = 0; $calls = 0; $v = 100;',
        '$throw = ' + ('true' if throwing else 'false') + ';',
    ]
    lines += [''] * (19 - len(lines))
    lines += [
        "$second = new Exception('print-owned-array');",
        "set_error_handler('print_array_handler', E_WARNING);",
        'try {',
        '    $v = (',
        '        print',
        '        take());',
    ]
    if throwing:
        lines += [
            "    echo 'BAD-R;';",
            '} catch (Throwable $e) {',
            "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', !isset($a), ':', $made === 1, ':', $calls === 1, ':', $seed === 99, ';';",
            '}',
        ]
    elif scalar:
        lines += [
            "    echo 'R:', $v === 1, ':', $a === [11,22], ':', $made === 1, ':', $calls === 0, ':', $seed === 0, ';';",
            "} catch (Throwable $e) { echo 'BAD-E;'; }",
        ]
    else:
        lines += [
            "    echo 'R:', $v === 1, ':', !isset($a), ':', $made === 1, ':', $calls === 1, ':', $seed === 99, ';';",
            "} catch (Throwable $e) { echo 'BAD-E;'; }",
        ]
    lines += [
        "finally { echo 'F;'; }",
        '$a = 8;',
        "echo 'END:', $a === 8, ':', $v === " + ('100' if throwing else '1') + ", ':', $made === 1, ':', $calls === " + ('0' if scalar else '1') + ", ';';",
    ]
    assert lines[19] == "$second = new Exception('print-owned-array');"
    assert lines[23] == '        print' and lines[24] == '        take());'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'print-acquired-array-false-default': source(),
    'print-acquired-array-pending-throw': source(throwing=True),
    'print-acquired-scalar-control': source(scalar=True),
}
