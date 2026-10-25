"""A live LEFT0 NaN callback must skip the AND right-side effect."""


def original(operator):
    lines = '''<?php
function k() { echo 'K;'; $GLOBALS['rhs'] = $GLOBALS['rhs'] + 1; return true; }
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $n, ':', $line, ':', $m, ';';
    $GLOBALS['x'] = 0.0;
    return false;
}
$x = NAN; $calls = 0; $rhs = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = (', '        $x', '        ' + operator + ' k());',
              "    echo 'R:', $v === false, ':', $x === 0.0, ':', $rhs === 0, ':', $calls === 1, ';';",
              "} catch (Throwable $e) { echo 'BAD-E;'; }", "finally { echo 'F;'; }", '$x = 8;',
              "echo 'END:', $v === false, ':', $x === 8, ':', $rhs === 0, ':', $calls === 1, ';';"]
    assert len(lines) == 30 and lines[23] == '        $x' and lines[24] == '        ' + operator + ' k());'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'short-nan-warning-symbolic-and-skip': original('&&'),
    'short-nan-warning-keyword-and-skip': original('and'),
}
