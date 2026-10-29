"""Saved LEFT integers and selected reference-cell types before object RIGHT."""
OPS = {'mod': '%', 'shl': '<<', 'shr': '>>', 'and': '&', 'or': '|', 'xor': '^'}
RESULTS = {'mod': 2, 'shl': 384, 'shr': 0, 'and': 4, 'or': 13, 'xor': 9}


def source(name, mode, shared_right=False):
    assert name in OPS and mode in ('repair', 'write-repair', 'retain', 'write-retain', 'throw')
    writes = mode.startswith('write-') or mode == 'throw'
    retains = mode.endswith('retain')
    throws = mode == 'throw'
    alias_test = '$alias === ' + ('99' if writes else '12.5')
    right_test = '$right instanceof stdClass' if retains else '$right === 5'
    left_type = 'int' if writes else 'float'
    lines = [
        '<?php',
        'function h($level, $message, $file, $line) {',
        "    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;",
        "    echo 'H:', $level === E_DEPRECATED, ':', $line === 24, ':', $message === 'Implicit conversion from float 12.5 to int loses precision', ':', $file === __FILE__, ':', $GLOBALS['left'] === 12.5, ':', $GLOBALS['alias'] === 12.5, ':', $GLOBALS['right'] instanceof stdClass, ';';",
        ("    $GLOBALS['alias'] = 99;" if writes else '    // Keep the old LEFT cell unchanged.'),
        "    $GLOBALS['left'] =& $GLOBALS['replacement'];",
        ('    // Retain the object in RIGHT.' if retains else "    $GLOBALS['right'] = 5;"),
        ("    throw $GLOBALS['failure'];" if throws else '    return false;'),
        '}',
        '$left = 12.5; $alias =& $left; $replacement = true; $right = new stdClass(); ' + ('$rightAlias =& $right; ' if shared_right else '') + '$calls = 0; $v = 100;',
    ]
    lines += [''] * (19 - len(lines))
    lines += [
        "$failure = new Exception('integer-left-reference-object');",
        "set_error_handler('h');",
        'try {',
        '    $v =',
        f'        $left {OPS[name]} $right;',
    ]
    if throws:
        lines += [
            "    echo 'BAD-R;';",
            '} catch (Throwable $e) {',
            "    echo 'C:', $e === $failure, ':', $e->getLine() === 20, ':', $e->getPrevious() === null, ':', $v === 100, ':', $calls === 1, ':', $left === true, ':', " + alias_test + ", ':', " + right_test + ", ';';",
        ]
    elif retains:
        lines += [
            "    echo 'BAD-R;';",
            '} catch (TypeError $e) {',
            "    echo 'C:', $e->getLine() === 24, ':', $e->getPrevious() === null, ':', $v === 100, ':', $calls === 1, ':', $left === true, ':', " + alias_test + ", ':', " + right_test + ", ':', $e->getMessage() === 'Unsupported operand types: " + left_type + " " + OPS[name] + " stdClass', ';';",
        ]
    else:
        lines += [
            f"    echo 'R:', $v === {RESULTS[name]}, ':', $calls === 1, ':', $left === true, ':', " + alias_test + ", ':', " + right_test + ", ';';",
            "} catch (Throwable $e) { echo 'BAD-E:', get_class($e), ';';",
        ]
    lines += [
        '}',
        "finally { echo 'F;'; }",
        'restore_error_handler();',
        "$alias = 7; echo 'A:', $alias === 7, ':', $left === true, ';';",
        "echo 'END:', $v === " + ('100' if retains or throws else str(RESULTS[name])) + ", ':', $calls === 1;",
    ]
    assert lines[19] == "$failure = new Exception('integer-left-reference-object');"
    assert lines[23] == f'        $left {OPS[name]} $right;'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    **{name + '-repair': source(name, 'repair') for name in OPS},
    **{name + '-write-repair': source(name, 'write-repair') for name in OPS},
    'mod-retain-float-typeerror': source('mod', 'retain'),
    'and-retain-int-typeerror': source('and', 'write-retain'),
    'shl-handler-throw': source('shl', 'throw'),
    'xor-handler-throw': source('xor', 'throw'),
    'both-shared-boundary': source('mod', 'write-repair', True),
}
EXPECTED_STDOUT = {
    name: b'H:1:1:1:1:1:1:1;' +
          (b'C:1:1:1:1:1:1:1:1;' if ('retain' in name or 'handler-throw' in name) else b'R:1:1:1:1:1;') +
          b'F;A:1:1;END:1:1'
    for name in CASES
}
