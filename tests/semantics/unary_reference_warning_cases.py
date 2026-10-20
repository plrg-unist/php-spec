"""Unary plus cancels delivery after its selected source reference retires."""


def original():
    lines = """<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ';';
    $GLOBALS['alias'] = 99; $GLOBALS['x'] =& $GLOBALS['replacement']; unset($GLOBALS['alias']);
    throw $GLOBALS['second'];
}
$tail = 'tail'; $x = '12.5' . $tail; $alias =& $x;
$replacement = 77; $calls = 0; $v = 100;""".splitlines()
    lines += [''] * (19 - len(lines))
    lines += ["$second = new Exception('unary-reference');", "set_error_handler('h', 2);", 'try {', '    $v = (', '        +', '        $x);',
              "    echo 'BAD-R;';", '} catch (Throwable $e) {',
              "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', $x === 77, ':', isset($alias) === false, ':', $calls === 1, ';';",
              "} finally { echo 'F;'; }", '$x = 8;',
              "echo 'END:', $replacement === 8, ':', isset($alias) === false, ':', $v === 100, ';';"]
    assert lines[19] == "$second = new Exception('unary-reference');"
    assert lines[23] == '        +' and lines[24] == '        $x);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'unary-reference-warning-throw-retired': original()}
