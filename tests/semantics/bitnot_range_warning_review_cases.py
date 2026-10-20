"""A captured out-of-range float survives source-CV removal during Warning."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $n, ':', $line, ':', $m, ';';
    $GLOBALS['x'] = 99; unset($GLOBALS['x']); return false;
}
$x = 9223372036854775808.0; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = (', '        ~', '        $x);',
              "    echo 'R:', $v, ':', $v === 9223372036854775807, ':', isset($x) === false, ':', $calls === 1, ';';",
              "} catch (Throwable $e) { echo 'BAD-E;';",
              "} finally { echo 'F;'; }", '$x = 8;',
              "echo 'END:', $v === 9223372036854775807, ':', $x === 8, ':', $calls === 1, ';';"]
    assert lines[23] == '        ~' and lines[24] == '        $x);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'bitnot-range-warning-wrap-max': original()}
