"""Explicit float wrapping differs from the handler's same-spelling string cast."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $n, ':', $line, ':', $m, ';';
    $GLOBALS['x'] = '9223372036854775808';
    echo 'T:', (int)$GLOBALS['x'], ';';
    return false;
}
$x = 9223372036854775808.0; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = (', '        (int)', '        $x);',
              "    echo 'R:', $v, ':', $v === PHP_INT_MIN, ':', $x === '9223372036854775808', ':', $calls === 1, ';';",
              "} catch (Throwable $e) { echo 'BAD-E;';",
              "} finally { echo 'F;'; }", '$x = 8;',
              "echo 'END:', $v === PHP_INT_MIN, ':', $x === 8, ':', $calls === 1, ';';"]
    assert lines[23] == '        (int)' and lines[24] == '        $x);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'int-cast-range-float-wrap-string-cap': original()}
