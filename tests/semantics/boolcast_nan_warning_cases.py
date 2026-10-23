"""Explicit Boolean cast rereads the same float CV after its NaN Warning."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $n, ':', $line, ':', $m, ';';
    $GLOBALS['x'] = 0.0;
    return false;
}
$x = NAN; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = (', '        (bool)', '        $x);',
              "    echo 'R:', $v, ':', $v === false, ':', $x === 0.0, ':', $calls === 1, ';';",
              "} catch (Throwable $e) { echo 'BAD-E;'; }", "finally { echo 'F;'; }", '$x = 8;',
              "echo 'END:', $v === false, ':', $x === 8, ':', $calls === 1, ';';"]
    assert len(lines) == 30 and lines[23] == '        (bool)' and lines[24] == '        $x);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'boolcast-nan-warning-live-float': original()}
