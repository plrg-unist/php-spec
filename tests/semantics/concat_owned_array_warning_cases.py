"""OP100 frozen candidates: acquired LEFT array in try-concat conversion."""


def source(throwing=False, scalar=False):
    returned = '7' if scalar else "$GLOBALS['a']"
    lines = [
        '<?php',
        'class OldText {',
        '    public function __toString(): string {',
        "        $GLOBALS['old_calls'] = $GLOBALS['old_calls'] + 1;",
        "        echo 'OLD;';",
        "        return 'OLD';",
        '    }',
        '}',
        'class NewText {',
        '    public function __toString(): string {',
        "        $GLOBALS['new_calls'] = $GLOBALS['new_calls'] + 1;",
        "        echo 'NEW;';",
        "        return 'NEW';",
        '    }',
        '}',
        'function concat_owned_handler($level, $message, $file, $line) {',
        "    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;",
        "    echo 'H:', $level, ':', $line, ':', $message, ':', $file === __FILE__, ';';",
        "    unset($GLOBALS['a']);",
        "    $GLOBALS['rhs'] = $GLOBALS['next'];",
        "    $GLOBALS['seed'] = 99;",
        "    if ($GLOBALS['throw']) throw $GLOBALS['second'];",
        '    return false;',
        '}',
        'function take() {',
        "    $GLOBALS['made'] = $GLOBALS['made'] + 1;",
        "    echo 'P;';",
        f'    return {returned};',
        '}',
        "$seed = 0; $a = [11, $seed + 22]; $made = 0; $calls = 0;",
        "$old_calls = 0; $new_calls = 0; $result = 'old';",
        '$rhs = new OldText(); $next = new NewText();',
        '$throw = ' + ('true' if throwing else 'false') + ';',
        "$second = new Exception('concat-owned-array');",
        "set_error_handler('concat_owned_handler', E_WARNING);",
        'try {',
        '    $result = take() . $rhs;',
    ]
    if throwing:
        lines += [
            "    echo 'BAD-R;';",
            '} catch (Throwable $e) {',
            "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $result === 'old', ':', !isset($a), ':', $made === 1, ':', $calls === 1, ':', $old_calls === 0, ':', $new_calls === 0, ':', $rhs === $next, ';';",
            '}',
        ]
    elif scalar:
        lines += [
            "    echo 'V:', $result, ';';",
            "    echo 'R:', $result === '7OLD', ':', $a === [11,22], ':', $made === 1, ':', $calls === 0, ':', $old_calls === 1, ':', $new_calls === 0, ':', $rhs !== $next, ';';",
            "} catch (Throwable $e) { echo 'BAD-E;'; }",
        ]
    else:
        lines += [
            "    echo 'V:', $result, ';';",
            "    echo 'R:', $result === 'ArrayNEW', ':', !isset($a), ':', $made === 1, ':', $calls === 1, ':', $old_calls === 0, ':', $new_calls === 1, ':', $rhs === $next, ':', $seed === 99, ';';",
            "} catch (Throwable $e) { echo 'BAD-E;'; }",
        ]
    lines += [
        "finally { echo 'F;'; }",
        '$a = 8;',
        "echo 'END:', $a === 8, ':', $result === " + ("'old'" if throwing else ("'7OLD'" if scalar else "'ArrayNEW'")) + ", ':', $made === 1, ':', $calls === " + ('0' if scalar else '1') + ", ';';",
    ]
    assert lines[33] == "$second = new Exception('concat-owned-array');"
    assert lines[36] == '    $result = take() . $rhs;'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'concat-acquired-left-array-false-default': source(),
    'concat-acquired-left-array-pending-throw': source(throwing=True),
    'concat-acquired-left-scalar-control': source(scalar=True),
}
