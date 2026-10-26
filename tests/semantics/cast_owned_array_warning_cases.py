"""OP99 originals: acquired by-value array result in explicit string cast."""


def source(throwing=False, scalar=False):
    result = '7' if scalar else "$GLOBALS['a']"
    lines = [
        '<?php',
        'function cast_array_handler($level, $message, $file, $line) {',
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
        "$seed = 0; $a = [11, $seed + 22]; $made = 0; $calls = 0; $v = 'old';",
        '$throw = ' + ('true' if throwing else 'false') + ';',
    ]
    lines += [''] * (19 - len(lines))
    lines += [
        "$second = new Exception('cast-owned-array');",
        "set_error_handler('cast_array_handler', E_WARNING);",
        'try {',
        '    $v = (',
        '        (string)',
        '        take());',
    ]
    if throwing:
        lines += [
            "    echo 'BAD-R;';",
            '} catch (Throwable $e) {',
            "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 'old', ':', !isset($a), ':', $made === 1, ':', $calls === 1, ':', $seed === 99, ';';",
            '}',
        ]
    elif scalar:
        lines += [
            "    echo 'R:', $v === '7', ':', $a === [11,22], ':', $made === 1, ':', $calls === 0, ':', $seed === 0, ';';",
            "} catch (Throwable $e) { echo 'BAD-E;'; }",
        ]
    else:
        lines += [
            "    echo 'R:', $v === 'Array', ':', !isset($a), ':', $made === 1, ':', $calls === 1, ':', $seed === 99, ';';",
            "} catch (Throwable $e) { echo 'BAD-E;'; }",
        ]
    lines += [
        "finally { echo 'F;'; }",
        '$a = 8;',
        "echo 'END:', $a === 8, ':', $v === " + ("'old'" if throwing else ("'7'" if scalar else "'Array'")) + ", ':', $made === 1, ':', $calls === " + ('0' if scalar else '1') + ", ';';",
    ]
    assert lines[19] == "$second = new Exception('cast-owned-array');"
    assert lines[23] == '        (string)' and lines[24] == '        take());'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'cast-acquired-array-false-default': source(),
    'cast-acquired-array-pending-throw': source(throwing=True),
    'cast-acquired-scalar-control': source(scalar=True),
}
