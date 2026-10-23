"""Explicit array cast copies the live float CV after its NaN Warning."""


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
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = (', '        (array)', '        $x);',
              "    echo 'R:', $v === [0.0], ':', $v[0] === 0.0, ':', $x === 0.0, ':', $calls === 1, ';';",
              "    $copy = $v; $copy[0] = 7; echo 'C:', $v[0] === 0.0, ':', $copy[0] === 7, ';';",
              "} catch (Throwable $e) { echo 'BAD-E;'; }", "finally { echo 'F;'; }", '$x = 8;',
              "echo 'END:', $v[0] === 0.0, ':', $x === 8, ':', $calls === 1, ';';"]
    assert len(lines) == 31 and lines[23] == '        (array)' and lines[24] == '        $x);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'arraycast-nan-warning-live-float': original()}
