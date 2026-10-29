"""Late owning LEFT values after its integer conversion has already succeeded."""

OPS = {'mod': '%', 'shl': '<<', 'shr': '>>', 'and': '&', 'or': '|', 'xor': '^'}


def source(op, shape, right_kind, mode='error'):
    assert op in OPS and shape in ('cv', 'cell', 'both')
    assert right_kind in ('object', 'array', 'string')
    assert mode in ('error', 'repair', 'throw')
    cell = shape != 'cv'
    target = 'leftAlias' if cell else 'left'
    rhs = {'object': 'new stdClass()', 'array': '[7]', 'string': "'not-numeric'"}[right_kind]
    right_type = {'object': 'stdClass', 'array': 'array', 'string': 'string'}[right_kind]
    left_test = '$left === 99' if cell else '$left instanceof LateLeft'
    lines = [
        '<?php',
        "class LateLeft { public function __destruct() { $GLOBALS['drops'] = $GLOBALS['drops'] + 1; echo 'D:', $GLOBALS['calls'] === 1, ';'; } }",
        'function h($level, $message, $file, $line) {',
        "    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;",
        "    echo 'H:', $level === E_DEPRECATED, ':', $line === 40, ':', $message === 'Implicit conversion from float 12.5 to int loses precision', ':', $file === __FILE__, ':', $GLOBALS['left'] === 12.5, ':', $GLOBALS['drops'] === 0, ';';",
        "    $GLOBALS['" + target + "'] = new LateLeft();",
        "    $GLOBALS['weak'] = WeakReference::create($GLOBALS['" + target + "']);",
        ("    $GLOBALS['left'] =& $GLOBALS['newLeft'];" if cell else '    // Keep the ordinary LEFT CV.'),
        ("    $GLOBALS['right'] =& $GLOBALS['newRight'];" if shape == 'both' else
         ("    $GLOBALS['right'] = " + ('0' if mode == 'throw' else '5') + ';' if mode != 'error' else '    // Keep the failed RIGHT input.')),
        ("    throw $GLOBALS['failure'];" if mode == 'throw' else '    return false;'),
        '}',
        '$left = 12.5; ' + ('$leftAlias =& $left; ' if cell else '') + '$right = ' + rhs + '; ' + ('$rightAlias =& $right; ' if shape == 'both' else '') + '$newLeft = 99; $newRight = 5; $calls = 0; $drops = 0; $weak = null; $v = 100;',
    ]
    lines += [''] * (35 - len(lines))
    lines += [
        "$failure = new Exception('late-left-object');",
        "set_error_handler('h');",
        'try {',
        '    $v =',
        f'        $left {OPS[op]} $right;',
    ]
    if mode == 'error':
        lines += [
            "    echo 'BAD-R;';",
            '} catch (TypeError $e) {',
            "    echo 'C:', $e->getMessage() === 'Unsupported operand types: LateLeft " + OPS[op] + ' ' + right_type + "', ':', $e->getLine() === 40, ':', $e->getPrevious() === null, ':', $v === 100, ':', $calls === 1, ':', " + left_test + ", ':', $weak->get() === $" + target + ", ':', $drops === 0, ';';",
        ]
    elif mode == 'repair':
        lines += [
            "    echo 'R:', $v === 384, ':', $calls === 1, ':', " + left_test + ", ':', $right === 5, ':', $weak->get() === $" + target + ", ':', $drops === 0, ';';",
            "} catch (Throwable $e) { echo 'BAD-E;';",
        ]
    else:
        lines += [
            "    echo 'BAD-R;';",
            '} catch (Throwable $e) {',
            "    echo 'C:', $e === $failure, ':', $e->getLine() === 36, ':', $e->getPrevious() === null, ':', $v === 100, ':', $calls === 1, ':', " + left_test + ", ':', $weak->get() === $" + target + ", ':', $drops === 0, ';';",
        ]
    lines += [
        '}',
        "finally { echo 'F;'; }",
        'restore_error_handler();',
        ("unset($leftAlias);" if cell else '$left = 7;'),
        "echo 'A:', $weak->get() === null, ':', $drops === 1, ':', " + ('$left === 99' if cell else '$left === 7') + ", ';';",
        "echo 'END:', $v === " + ('384' if mode == 'repair' else '100') + ", ':', $calls === 1;",
    ]
    assert lines[35] == "$failure = new Exception('late-left-object');"
    assert lines[39] == f'        $left {OPS[op]} $right;'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    **{op + '-cv-object-error': source(op, 'cv', 'object') for op in OPS},
    **{op + '-cell-array-error': source(op, 'cell', 'array') for op in OPS},
    'mod-cell-string-error': source('mod', 'cell', 'string'),
    'xor-both-object-error': source('xor', 'both', 'object'),
    'shl-cv-repair-control': source('shl', 'cv', 'object', 'repair'),
    'mod-cell-handler-throw': source('mod', 'cell', 'object', 'throw'),
}
EXPECTED_STDOUT = {
    name: b'H:1:1:1:1:1:1;' + (b'R:1:1:1:1:1:1;' if name == 'shl-cv-repair-control' else b'C:1:1:1:1:1:1:1:1;') + b'F;D:1;A:1:1:1;END:1:1'
    for name in CASES
}


def expected_stderr(name, path):
    return b'' if name.endswith('handler-throw') else b'Deprecated: Implicit conversion from float 12.5 to int loses precision in ' + bytes(path) + b' on line 40\n'
