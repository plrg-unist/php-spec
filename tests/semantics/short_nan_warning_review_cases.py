"""Live false LEFT enters OR's right call; a pending throw prevents AND's call."""


def original(operator, throws=False):
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $n, ':', $line, ':', $m, ';';'''.splitlines()
    if throws:
        lines += ["    $GLOBALS['x'] = 1.0;", "    throw $GLOBALS['second'];"]
    else:
        lines += ["    $GLOBALS['x'] = 0.0;", '    return false;']
    lines += ['}', 'function k() {', "    $GLOBALS['rhs'] = $GLOBALS['rhs'] + 1;",
              "    echo 'K;';", "    $GLOBALS['x'] = 2.0;", '    return false;', '}',
              '$x = NAN; $calls = 0; $rhs = 0; $v = 100;']
    lines += [''] * ((19 if throws else 20) - len(lines))
    if throws:
        lines += ["$second = new Exception('short');"]
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = (', '        $x ' + operator, '        k());']
    if throws:
        lines += ["    echo 'BAD-R;';", '} catch (Throwable $e) {',
                  "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', $x === 1.0, ':', $calls === 1, ':', $rhs === 0, ';';",
                  "} finally { echo 'F;'; }", '$x = 8;',
                  "echo 'END:', $x === 8, ':', $v === 100, ':', $calls === 1, ':', $rhs === 0, ';';"]
    else:
        lines += ["    echo 'R:', $v === false, ':', $x === 2.0, ':', $calls === 1, ':', $rhs === 1, ';';",
                  "} catch (Throwable $e) { echo 'BAD-E;'; }", "finally { echo 'F;'; }", '$x = 8;',
                  "echo 'END:', $x === 8, ':', $v === false, ':', $calls === 1, ':', $rhs === 1, ';';"]
    assert lines[23] == '        $x ' + operator and lines[24] == '        k());'
    if throws:
        assert lines[19] == "$second = new Exception('short');"
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'short-nan-warning-symbolic-or-enter': original('||'),
    'short-nan-warning-keyword-or-enter': original('or'),
    'short-nan-warning-supplied-throw': original('&&', True),
}
