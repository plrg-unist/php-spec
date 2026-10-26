"""OP101 frozen candidates: acquired RIGHT array after LEFT Stringable."""


def source(throwing=False, scalar=False):
    returned = '7' if scalar else "$GLOBALS['a']"
    lines = [
        '<?php',
        'class LeftText {',
        '    public function __toString(): string {',
        "        $GLOBALS['left_calls'] = $GLOBALS['left_calls'] + 1;",
        "        echo 'L;';",
        "        $GLOBALS['left'] = $GLOBALS['other'];",
        "        return 'L';",
        '    }',
        '}',
        'class OtherText {',
        '    public function __toString(): string {',
        "        $GLOBALS['other_calls'] = $GLOBALS['other_calls'] + 1;",
        "        echo 'OTHER;';",
        "        return 'OTHER';",
        '    }',
        '}',
        'function right_array_handler($level, $message, $file, $line) {',
        "    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;",
        "    echo 'H:', $level, ':', $line, ':', $message, ':', $file === __FILE__, ';';",
        "    unset($GLOBALS['a']);",
        "    if ($GLOBALS['throw']) throw $GLOBALS['second'];",
        '    return false;',
        '}',
        'function take() {',
        "    $GLOBALS['made'] = $GLOBALS['made'] + 1;",
        "    echo 'P;';",
        f'    return {returned};',
        '}',
        "$seed = 0; $a = [11, $seed + 22]; $made = 0; $calls = 0;",
        "$left = new LeftText(); $other = new OtherText();",
        "$left_calls = 0; $other_calls = 0; $result = 'old';",
        '$throw = ' + ('true' if throwing else 'false') + ';',
        "$second = new Exception('concat-acquired-right-array');",
        "set_error_handler('right_array_handler', E_WARNING);",
        'try {',
        '    $result = $left . take();',
    ]
    if throwing:
        lines += [
            "    echo 'BAD-R;';",
            '} catch (Throwable $e) {',
            "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $result === 'old', ':', !isset($a), ':', $made === 1, ':', $calls === 1, ':', $left_calls === 1, ':', $other_calls === 0, ':', $left === $other, ';';",
            '}',
        ]
    elif scalar:
        lines += [
            "    echo 'V:', $result, ';';",
            "    echo 'R:', $result === 'L7', ':', $a === [11,22], ':', $made === 1, ':', $calls === 0, ':', $left_calls === 1, ':', $other_calls === 0, ':', $left === $other, ';';",
            "} catch (Throwable $e) { echo 'BAD-E;'; }",
        ]
    else:
        lines += [
            "    echo 'V:', $result, ';';",
            "    echo 'R:', $result === 'LArray', ':', !isset($a), ':', $made === 1, ':', $calls === 1, ':', $left_calls === 1, ':', $other_calls === 0, ':', $left === $other, ';';",
            "} catch (Throwable $e) { echo 'BAD-E;'; }",
        ]
    lines += [
        "finally { echo 'F;'; }",
        '$a = 8;',
        "echo 'END:', $a === 8, ':', $result === " + ("'old'" if throwing else ("'L7'" if scalar else "'LArray'")) + ", ':', $made === 1, ':', $left_calls === 1, ':', $other_calls === 0, ';';",
    ]
    assert lines[32] == "$second = new Exception('concat-acquired-right-array');"
    assert lines[35] == '    $result = $left . take();'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'concat-acquired-right-array-false-default': source(),
    'concat-acquired-right-array-pending-throw': source(throwing=True),
    'concat-acquired-right-scalar-control': source(scalar=True),
}
