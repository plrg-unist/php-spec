"""Direct BOOLNOT reads the same float CV again after its NaN Warning."""


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
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = (', '        !', '        $x);',
              "    echo 'R:', $v, ':', $v === true, ':', $x === 0.0, ':', $calls === 1, ';';",
              "} catch (Throwable $e) { echo 'BAD-E;'; }", "finally { echo 'F;'; }", '$x = 8;',
              "echo 'END:', $v === true, ':', $x === 8, ':', $calls === 1, ';';"]
    assert len(lines) == 30 and lines[23] == '        !' and lines[24] == '        $x);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'boolnot-nan-warning-live-float': original()}
