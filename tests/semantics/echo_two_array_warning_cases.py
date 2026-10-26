"""OP97 originals: first echo array warning creates the second echo array."""


def source(throw_at):
    lines = [
        '<?php',
        'function two_array_handler($level, $message, $file, $line) {',
        "    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;",
        "    $n = $GLOBALS['calls'];",
        "    echo 'H:', $n, ':', $level, ':', $line, ':', $message, ':', $file === __FILE__, ';';",
        '    if ($n === 1) {',
        "        $GLOBALS['b'] = [33, $GLOBALS['calls'] + 43];",
        "        $GLOBALS['tag'] = 'after1';",
        "        $GLOBALS['a'] = 99;",
        "        unset($GLOBALS['a']);",
        '    } else {',
        "        $GLOBALS['tag'] = 'after2';",
        "        $GLOBALS['b'] = 99;",
        "        unset($GLOBALS['b']);",
        '    }',
        "    if ($n === $GLOBALS['throw_at']) throw $GLOBALS['second'];",
        '    return false;',
        '}',
        'function later() {',
        "    $GLOBALS['later_calls'] = $GLOBALS['later_calls'] + 1;",
        "    echo 'L;';",
        "    return $GLOBALS['tag'];",
        '}',
        f"$a = [11, 22]; $b = 7; $tag = 'before'; $calls = 0; $later_calls = 0; $throw_at = {throw_at};",
    ]
    lines += [''] * (27 - len(lines))
    lines += [
        "$second = new Exception('two-array');",
        "set_error_handler('two_array_handler', E_WARNING);",
        'try {',
        '    echo',
        '        $a,',
        '        $b,',
        "        '|',",
        '        later();',
    ]
    if throw_at == 0:
        lines += [
            "    echo 'R:', $calls === 2, ':', $later_calls === 1, ':', $tag === 'after2', ':', !isset($a), ':', !isset($b), ';';",
            "} catch (Throwable $e) { echo 'BAD-E;'; }",
        ]
    else:
        lines += [
            "    echo 'BAD-R;';",
            '} catch (Throwable $e) {',
            "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $calls === " + str(throw_at) + ", ':', $later_calls === 0, ':', !isset($a), ':', " + ("isset($b) && $b === [33, 44]" if throw_at == 1 else "!isset($b)") + ", ':', $tag === 'after" + str(throw_at) + "', ';';",
            '}',
        ]
    lines += [
        "finally { echo 'F;'; }",
        "$a = 8;",
        "echo 'END:', $a === 8, ':', $calls === " + str(2 if throw_at == 0 else throw_at) + ", ':', $later_calls === " + str(1 if throw_at == 0 else 0) + ", ';';",
    ]
    assert lines[27] == "$second = new Exception('two-array');"
    assert lines[31] == '        $a,'
    assert lines[32] == '        $b,'
    assert lines[34] == '        later();'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'echo-two-arrays-both-default': source(0),
    'echo-two-arrays-first-throw': source(1),
    'echo-two-arrays-second-throw': source(2),
}
