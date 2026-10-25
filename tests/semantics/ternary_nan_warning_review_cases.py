"""A falsy live shorthand condition selects a value; its pending throw selects none."""


def original(throws):
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $n, ':', $line, ':', $m, ';';
    $GLOBALS['x'] = 0.0;'''.splitlines()
    lines += ["    throw $GLOBALS['second'];" if throws else '    return false;']
    lines += ['}', 'function k() {', "    $GLOBALS['rhs'] = $GLOBALS['rhs'] + 1;",
              "    echo 'K;';", "    $GLOBALS['x'] = 2.0;", '    return 7;', '}',
              '$x = NAN; $calls = 0; $rhs = 0; $v = 100;']
    lines += [''] * ((19 if throws else 20) - len(lines))
    if throws:
        lines += ["$second = new Exception('ternary');"]
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = (', '        $x', '        ?: k());']
    if throws:
        lines += ["    echo 'BAD-R;';", '} catch (Throwable $e) {',
                  "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', $x === 0.0, ':', $calls === 1, ':', $rhs === 0, ';';",
                  "} finally { echo 'F;'; }", '$x = 8;',
                  "echo 'END:', $x === 8, ':', $v === 100, ':', $calls === 1, ':', $rhs === 0, ';';"]
    else:
        lines += ["    echo 'R:', $v === 7, ':', $x === 2.0, ':', $calls === 1, ':', $rhs === 1, ';';",
                  "} catch (Throwable $e) { echo 'BAD-E;'; }", "finally { echo 'F;'; }", '$x = 8;',
                  "echo 'END:', $x === 8, ':', $v === 7, ':', $calls === 1, ':', $rhs === 1, ';';"]
    assert lines[23] == '        $x' and lines[24] == '        ?: k());'
    if throws:
        assert lines[19] == "$second = new Exception('ternary');"
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'ternary-nan-warning-fallback-value': original(False),
    'ternary-nan-warning-supplied-throw': original(True),
}
