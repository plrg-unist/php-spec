"""Self compound ADD reads the current same CV after its first Warning."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m, ';';
    if ($GLOBALS['calls'] === 1) {
        $GLOBALS['x'] = '5.5' . $GLOBALS['tail'];
        return true;
    }
    $GLOBALS['x'] = 88;
    return false;
}
$tail = 'tail';
$x = '12.5' . $tail; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = ($x', '        +=', '        $x);',
              "    echo 'R:', $v, ':', $v === 18.0, ':', $x === 18.0, ':', $calls === 2, ';';",
              "} catch (Throwable $e) { echo 'BAD-E;';",
              "} finally { echo 'F;'; }", '$x = 8;',
              "echo 'END:', $v === 18.0, ':', $x === 8, ':', $calls === 2, ';';"]
    assert lines[22] == '    $v = ($x' and lines[23] == '        +=' and lines[24] == '        $x);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'addassign-self-warning-current-rhs': original()}
