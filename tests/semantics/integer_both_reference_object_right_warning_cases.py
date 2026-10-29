"""Both borrowed cells through integer conversion and two CV rebinds."""
from integer_reference_left_object_right_warning_cases import CASES as LEFT_CASES, EXPECTED_STDOUT as LEFT_STDOUT

OPS = {'mod': '%', 'shl': '<<', 'shr': '>>', 'and': '&', 'or': '|', 'xor': '^'}
LIVE_RESULTS = {'mod': 2, 'shl': 384, 'shr': 0, 'and': 4, 'or': 13, 'xor': 9}
OLD_RESULTS = {'and': 0, 'or': 14, 'xor': 14}


def source(name, mode):
    assert name in OPS and mode in ('rebind', 'write-both', 'left-int', 'left-string', 'throw')
    bitwise = name in OLD_RESULTS
    throws = mode == 'throw'
    fails = bitwise and mode in ('rebind', 'left-int', 'left-string')
    result = OLD_RESULTS[name] if bitwise and mode == 'write-both' else LIVE_RESULTS[name]
    left_value = "'old-left'" if mode == 'left-string' else ('99' if mode in ('write-both', 'left-int', 'throw') else '12.5')
    left_type = 'string' if mode == 'left-string' else ('int' if mode in ('write-both', 'left-int', 'throw') else 'float')
    right_value = '5.5' if throws else ('2' if mode == 'write-both' else None)
    new_right = '0' if throws else '5'
    left_test = '$leftAlias === ' + left_value
    right_test = '$rightAlias === ' + right_value if right_value else '$rightAlias instanceof stdClass'
    lines = [
        '<?php',
        'function h($level, $message, $file, $line) {',
        "    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;",
        "    echo 'H:', $level === E_DEPRECATED, ':', $line === 24, ':', $message === 'Implicit conversion from float 12.5 to int loses precision', ':', $file === __FILE__, ':', $GLOBALS['left'] === 12.5, ':', $GLOBALS['leftAlias'] === 12.5, ':', $GLOBALS['right'] === $GLOBALS['rightAlias'], ':', $GLOBALS['rightAlias'] instanceof stdClass, ';';",
        ("    $GLOBALS['leftAlias'] = " + left_value + ';' if mode != 'rebind' else '    // Keep the old LEFT payload.'),
        ("    $GLOBALS['rightAlias'] = " + right_value + ';' if right_value else '    // Keep the old RIGHT object alive.'),
        "    $GLOBALS['left'] =& $GLOBALS['newLeft'];",
        "    $GLOBALS['right'] =& $GLOBALS['newRight'];",
        ("    throw $GLOBALS['failure'];" if throws else '    return false;'),
        '}',
        '$left = 12.5; $leftAlias =& $left; $right = new stdClass(); $rightAlias =& $right; $newLeft = true; $newRight = ' + new_right + '; $calls = 0; $v = 100;',
    ]
    lines += [''] * (19 - len(lines))
    lines += [
        "$failure = new Exception('integer-both-reference');",
        "set_error_handler('h');",
        'try {',
        '    $v =',
        f'        $left {OPS[name]} $right;',
    ]
    if throws:
        lines += [
            "    echo 'BAD-R;';",
            '} catch (Throwable $e) {',
            "    echo 'C:', $e === $failure, ':', $e->getLine() === 20, ':', $e->getPrevious() === null, ':', $v === 100, ':', $calls === 1, ':', $left === true, ':', $right === " + new_right + ", ':', " + left_test + ", ':', " + right_test + ", ';';",
        ]
    elif fails:
        lines += [
            "    echo 'BAD-R;';",
            '} catch (TypeError $e) {',
            "    echo 'C:', $e->getLine() === 24, ':', $e->getPrevious() === null, ':', $v === 100, ':', $calls === 1, ':', $left === true, ':', $right === 5, ':', " + left_test + ", ':', " + right_test + ", ':', $e->getMessage() === 'Unsupported operand types: " + left_type + " " + OPS[name] + " stdClass', ';';",
        ]
    else:
        lines += [
            f"    echo 'R:', $v === {result}, ':', $calls === 1, ':', $left === true, ':', $right === 5, ':', " + left_test + ", ':', " + right_test + ", ';';",
            "} catch (Throwable $e) { echo 'BAD-E:', get_class($e), ';';",
        ]
    lines += [
        '}',
        "finally { echo 'F;'; }",
        'restore_error_handler();',
        "$leftAlias = 7; $rightAlias = 3; echo 'A:', $left === true, ':', $right === " + new_right + ", ':', $leftAlias === 7, ':', $rightAlias === 3, ';';",
        "echo 'END:', $v === " + ('100' if fails or throws else str(result)) + ", ':', $calls === 1;",
    ]
    assert lines[19] == "$failure = new Exception('integer-both-reference');"
    assert lines[23] == f'        $left {OPS[name]} $right;'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    **{name + '-rebind': source(name, 'rebind') for name in OPS},
    **{name + '-write-both': source(name, 'write-both') for name in OPS},
    'and-left-int-typeerror': source('and', 'left-int'),
    'or-left-string-typeerror': source('or', 'left-string'),
    'mod-handler-throw': source('mod', 'throw'),
    'xor-handler-throw': source('xor', 'throw'),
    'promoted-op108-both-cell': LEFT_CASES['both-shared-boundary'],
}
EXPECTED_STDOUT = {
    name: b'H:1:1:1:1:1:1:1:1;' +
          (b'C:1:1:1:1:1:1:1:1:1;' if ('typeerror' in name or 'handler-throw' in name or (name.split('-')[0] in OLD_RESULTS and name.endswith('-rebind'))) else b'R:1:1:1:1:1:1;') +
          b'F;A:1:1:1:1;END:1:1'
    for name in CASES if name != 'promoted-op108-both-cell'
}
EXPECTED_STDOUT['promoted-op108-both-cell'] = LEFT_STDOUT['both-shared-boundary']
