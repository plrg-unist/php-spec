"""Integer operators with a borrowed reference cell containing a stdClass RHS."""
from integer_object_right_warning_cases import CASES as PLAIN_CASES


OPS = {'mod': '%', 'shl': '<<', 'shr': '>>', 'and': '&', 'or': '|', 'xor': '^'}
LIVE_RESULTS = {'mod': 2, 'shl': 384, 'shr': 0, 'and': 4, 'or': 13, 'xor': 9}
CELL_RESULTS = {'and': 0, 'or': 14, 'xor': 14}


def source(name, mode):
    assert name in OPS and mode in ('rebind', 'write-rebind', 'retain', 'throw')
    bitwise = name in CELL_RESULTS
    throws = mode == 'throw'
    fails = mode == 'retain' or (bitwise and mode == 'rebind')
    result = CELL_RESULTS[name] if bitwise and mode == 'write-rebind' else LIVE_RESULTS[name]
    alias_test = "$alias === 2" if mode == 'write-rebind' else "$alias instanceof stdClass"
    right_test = "$right instanceof stdClass" if mode == 'retain' else "$right === 5"
    lines = [
        '<?php',
        'function h($level, $message, $file, $line) {',
        "    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;",
        "    echo 'H:', $level === E_DEPRECATED, ':', $line === 24, ':', $message === 'Implicit conversion from float 12.5 to int loses precision', ':', $file === __FILE__, ':', $GLOBALS['left'] === 12.5, ':', $GLOBALS['right'] === $GLOBALS['alias'], ':', $GLOBALS['alias'] instanceof stdClass, ';';",
        "    $GLOBALS['left'] = 99.5;",
        ("    $GLOBALS['alias'] = 2;" if mode == 'write-rebind' else '    // Keep the old object alive through its outside alias.'),
        ("    $GLOBALS['right'] =& $GLOBALS['replacement'];" if mode != 'retain' else '    // Leave RIGHT attached to the old cell.'),
        ("    throw $GLOBALS['failure'];" if throws else '    return false;'),
        '}',
        '$left = 12.5; $right = new stdClass(); $alias =& $right; $replacement = 5; $calls = 0; $v = 100;',
    ]
    lines += [''] * (19 - len(lines))
    lines += [
        "$failure = new Exception('integer-reference-object');",
        "set_error_handler('h');",
        'try {',
        '    $v =',
        f'        $left {OPS[name]} $right;',
    ]
    if throws:
        lines += [
            "    echo 'BAD-R;';",
            '} catch (Throwable $e) {',
            "    echo 'C:', $e === $failure, ':', $e->getLine() === 20, ':', $e->getPrevious() === null, ':', $v === 100, ':', $calls === 1, ':', $left === 99.5, ':', " + right_test + ", ':', " + alias_test + ", ';';",
        ]
    elif fails:
        lines += [
            "    echo 'BAD-R;';",
            '} catch (TypeError $e) {',
            "    echo 'C:', $e->getLine() === 24, ':', $e->getPrevious() === null, ':', $v === 100, ':', $calls === 1, ':', $left === 99.5, ':', " + right_test + ", ':', " + alias_test + ", ':', $e->getMessage() === 'Unsupported operand types: float " + OPS[name] + " stdClass', ';';",
        ]
    else:
        lines += [
            f"    echo 'R:', $v === {result}, ':', $calls === 1, ':', $left === 99.5, ':', " + right_test + ", ':', " + alias_test + ", ';';",
            "} catch (Throwable $e) { echo 'BAD-E:', get_class($e), ';';",
        ]
    lines += [
        '}',
        "finally { echo 'F;'; }",
        'restore_error_handler();',
        "$alias = 7; echo 'A:', $alias === 7, ':', $right === " + ('7' if mode == 'retain' else '5') + ", ';';",
        "echo 'END:', $v === " + ('100' if fails or throws else str(result)) + ", ':', $calls === 1;",
    ]
    assert lines[19] == "$failure = new Exception('integer-reference-object');"
    assert lines[23] == f'        $left {OPS[name]} $right;'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    **{name + '-rebind': source(name, 'rebind') for name in OPS},
    **{name + '-write-rebind': source(name, 'write-rebind') for name in OPS},
    'mod-retain-typeerror': source('mod', 'retain'),
    'and-retain-typeerror': source('and', 'retain'),
    'shl-handler-throw': source('shl', 'throw'),
    'xor-handler-throw': source('xor', 'throw'),
    'plain-mod-repair-control': PLAIN_CASES['mod-replace'],
}

EXPECTED_STDOUT = {
    name: b'H:1:1:1:1:1:1:1;' +
          (b'C:1:1:1:1:1:1:1:1;' if ('retain' in name or 'handler-throw' in name or (name.split('-')[0] in CELL_RESULTS and name.endswith('-rebind') and '-write-' not in name)) else b'R:1:1:1:1:1;') +
          b'F;A:1:1;END:1:1'
    for name in CASES if name != 'plain-mod-repair-control'
}
EXPECTED_STDOUT['plain-mod-repair-control'] = b'H:1:1:1:1:1:1;R:1:1:1:1;F;END:1:1'
