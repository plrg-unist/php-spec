"""Supplied XOR-handler exceptions cancel delivery at either truth stage."""


def original(first):
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m, ';';'''.splitlines()
    if first:
        lines += ["    $GLOBALS['a'] = 0.0;", "    set_error_handler('h', 8192);",
                  "    throw $GLOBALS['second'];"]
        right, count, right_check, label = 'NAN', 1, '$b !== $b', 'xor-first'
    else:
        lines += ["    if ($GLOBALS['calls'] === 1) {", "        $GLOBALS['a'] = 1.0;",
                  "        $GLOBALS['b'] = NAN;", '        return true;', '    }',
                  "    $GLOBALS['a'] = 0.0;", "    $GLOBALS['b'] = 0.0;",
                  "    throw $GLOBALS['second'];"]
        right, count, right_check, label = '0.0', 2, '$b === 0.0', 'xor-second'
    lines += ['}', '$a = NAN; $b = ' + right + '; $calls = 0; $v = 100;']
    lines += [''] * (19 - len(lines))
    lines += ["$second = new Exception('" + label + "');", "set_error_handler('h', 2);", 'try {',
              '    $v = (', '        $a xor', '        $b);',
              "    echo 'BAD-R;';", '} catch (Throwable $e) {',
              "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', $a === 0.0, ':', " + right_check + ", ':', $calls === " + str(count) + ", ';';",
              "} finally { echo 'F;'; }", '$a = 8; $b = 9;',
              "echo 'END:', $a === 8, ':', $b === 9, ':', $v === 100, ':', $calls === " + str(count) + ", ';';"]
    assert lines[19] == "$second = new Exception('" + label + "');"
    assert lines[23] == '        $a xor' and lines[24] == '        $b);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'xor-nan-warning-second-supplied-throw': original(False),
    'xor-nan-warning-first-supplied-throw-masked': original(True),
}
