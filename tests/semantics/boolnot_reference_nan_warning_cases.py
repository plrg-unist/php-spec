"""BOOL_NOT rereads a saved inner reference cell after the source CV rebinds."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $n, ':', $line, ':', $m, ';';
    $GLOBALS['alias'] = 0.0;
    $GLOBALS['x'] =& $GLOBALS['replacement'];
    return false;
}
$x = NAN; $alias =& $x; $replacement = 1.0; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = (', '        !', '        $x);',
              "    echo 'R:', $v === true, ':', $alias === 0.0, ':', $x === 1.0, ':', $replacement === 1.0, ':', $calls === 1, ';';",
              "} catch (Throwable $e) { echo 'BAD-E;'; }", "finally { echo 'F;'; }", '$x = 8;',
              "echo 'END:', $replacement === 8, ':', $alias === 0.0, ':', $v === true, ':', $calls === 1, ';';"]
    assert len(lines) == 30 and lines[23] == '        !' and lines[24] == '        $x);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'boolnot-reference-nan-warning-rebound': original()}
