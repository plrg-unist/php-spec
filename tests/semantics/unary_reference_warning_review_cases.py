"""Unary minus keeps signed zero after its selected reference retires."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ';';
    $GLOBALS['alias'] = 99;
    $GLOBALS['x'] =& $GLOBALS['replacement'];
    unset($GLOBALS['alias']);
    return false;
}
$tail = 'tail'; $x = '0.0' . $tail;
$alias =& $x; $replacement = 77; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 2);", 'try {', '    $v =', '        -', '        $x;',
              "    echo 'R:', $v, ':', $v === -0.0, ':', $x === 77, ':', $replacement === 77, ':', isset($alias) === false, ':', $calls === 1, ';';",
              "} catch (Throwable $e) { echo 'BAD-E:', $e->getLine(), ';';",
              "} finally { echo 'F;'; }", '$x = 8;',
              "echo 'END:', $replacement === 8, ':', isset($alias) === false, ':', $v === -0.0, ':', $calls === 1, ';';"]
    assert lines[23] == '        -' and lines[24] == '        $x;'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'unary-reference-warning-retired-negative-zero': original()}
