"""OP102 frozen candidates: acquired RHS array in used concat assignment."""


def source(throwing=False, scalar=False):
    returned = '7' if scalar else "$GLOBALS['a']"
    lines = [
        '<?php',
        'function h($level, $message, $file, $line) {',
        "    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;",
        "    echo 'H:', $level, ':', $line, ':', $message, ':', $file === __FILE__, ':', $GLOBALS['lhs'] === 'A', ';';",
        "    $GLOBALS['lhs'] = 'B';",
        "    unset($GLOBALS['a']);",
        "    if ($GLOBALS['throw']) throw $GLOBALS['second'];",
        '    return false;',
        '}',
        'function take() {',
        "    $GLOBALS['made'] = $GLOBALS['made'] + 1;",
        "    echo 'P;';",
        f'    return {returned};',
        '}',
        '$seed = 0;',
        '$a = [11, $seed + 22];',
        '$made = 0; $calls = 0;',
        "$lhs = 'A'; $value = 'old';",
        '$throw = ' + ('true' if throwing else 'false') + ';',
        "$second = new Exception('concatassign-acquired-right-array');",
        "set_error_handler('h', E_WARNING);",
        'try {',
        '    $value = ($lhs .= take());',
    ]
    if throwing:
        lines += [
            "    echo 'BAD-R;';",
            '} catch (Throwable $e) {',
            "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $lhs === 'B', ':', $value === 'old', ':', !isset($a), ':', $made === 1, ':', $calls === 1, ';';",
            '}',
        ]
    elif scalar:
        lines += [
            "    echo 'V:', $value, ';';",
            "    echo 'R:', $lhs === 'A7', ':', $value === 'A7', ':', $a === [11,22], ':', $made === 1, ':', $calls === 0, ';';",
            "} catch (Throwable $e) { echo 'BAD-E;'; }",
        ]
    else:
        lines += [
            "    echo 'V:', $value, ';';",
            "    echo 'R:', $lhs === 'AArray', ':', $value === 'AArray', ':', !isset($a), ':', $made === 1, ':', $calls === 1, ';';",
            "} catch (Throwable $e) { echo 'BAD-E;'; }",
        ]
    lines += [
        "finally { echo 'F;'; }",
        '$a = 8;',
        "echo 'END:', $a === 8, ':', $lhs === " + ("'B'" if throwing else ("'A7'" if scalar else "'AArray'")) + ", ':', $value === " + ("'old'" if throwing else ("'A7'" if scalar else "'AArray'")) + ", ':', $made === 1, ':', $calls === " + ('0' if scalar else '1') + ", ';';",
    ]
    assert lines[19] == "$second = new Exception('concatassign-acquired-right-array');"
    assert lines[22] == '    $value = ($lhs .= take());'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'concatassign-acquired-right-array-false-default': source(),
    'concatassign-acquired-right-array-pending-throw': source(throwing=True),
    'concatassign-acquired-right-scalar-control': source(scalar=True),
}
