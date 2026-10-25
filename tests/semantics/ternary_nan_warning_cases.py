"""JMP_SET copies the live selected float after its NaN Warning callback."""


def original():
    lines = '''<?php
function k() { echo 'K;'; $GLOBALS['rhs'] = $GLOBALS['rhs'] + 1; $GLOBALS['x'] = 2.0; return 7; }
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $n, ':', $line, ':', $m, ';';
    $GLOBALS['x'] = 1.0;
    return false;
}
$x = NAN; $calls = 0; $rhs = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = (', '        $x', '        ?: k());',
              "    echo 'R:', $v === 1.0, ':', $x === 1.0, ':', $rhs === 0, ':', $calls === 1, ';';",
              "} catch (Throwable $e) { echo 'BAD-E;'; }", "finally { echo 'F;'; }", '$x = 8;',
              "echo 'END:', $v === 1.0, ':', $x === 8, ':', $rhs === 0, ':', $calls === 1, ';';"]
    assert len(lines) == 30 and lines[23] == '        $x' and lines[24] == '        ?: k());'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'ternary-nan-warning-live-value': original()}
