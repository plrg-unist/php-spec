"""Self addition converts the changed CV again before supplied second throw."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m, ';';
    if ($GLOBALS['calls'] === 1) { $GLOBALS['x'] = '5.5tail'; return true; }
    $GLOBALS['x'] = 88;
    throw $GLOBALS['second'];
}
$x = '12.5tail'; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (19 - len(lines))
    lines += ["$second = new Exception('addassign-self');", "set_error_handler('h', 2);", 'try {', '    $v = ($x', '        +=', '        $x);',
              "    echo 'BAD-R;';", '} catch (Throwable $e) {',
              "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', $x === 88, ':', $calls === 2, ';';",
              "} finally { echo 'F;'; }", '$x = 8;',
              "echo 'END:', $x === 8, ':', $v === 100, ':', $calls === 2, ';';"]
    assert lines[19] == "$second = new Exception('addassign-self');"
    assert lines[22] == '    $v = ($x' and lines[23] == '        +=' and lines[24] == '        $x);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'addassign-self-warning-second-throw': original()}
