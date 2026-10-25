"""Retained inner reference cells survive source removal and supplied throw."""


def original(throws):
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $n, ':', $line, ':', $m, ';';
    $GLOBALS['alias'] = 0.0;
    unset($GLOBALS['x']);'''.splitlines()
    if throws:
        lines += ["    $GLOBALS['x'] =& $GLOBALS['replacement'];",
                  "    throw $GLOBALS['second'];"]
    else:
        lines += ['    return false;']
    lines += ['}', '$x = NAN; $alias =& $x; $replacement = 1.0; $calls = 0; $v = 100;']
    lines += [''] * ((19 if throws else 20) - len(lines))
    if throws:
        lines += ["$second = new Exception('boolnot-ref');"]
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = (', '        !', '        $x);']
    if throws:
        lines += ["    echo 'BAD-R;';", '} catch (Throwable $e) {',
                  "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', $alias === 0.0, ':', $x === 1.0, ':', $replacement === 1.0, ':', $calls === 1, ';';",
                  "} finally { echo 'F;'; }", '$alias = 7; $x = 8;',
                  "echo 'END:', $alias === 7, ':', $x === 8, ':', $replacement === 8, ':', $v === 100, ':', $calls === 1, ';';"]
    else:
        lines += ["    echo 'R:', $v === true, ':', $alias === 0.0, ':', isset($x) === false, ':', $calls === 1, ';';",
                  "} catch (Throwable $e) { echo 'BAD-E;'; }", "finally { echo 'F;'; }", '$alias = 8;',
                  "echo 'END:', $alias === 8, ':', isset($x) === false, ':', $v === true, ':', $calls === 1, ';';"]
    assert lines[23] == '        !' and lines[24] == '        $x);'
    if throws:
        assert lines[19] == "$second = new Exception('boolnot-ref');"
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'boolnot-reference-nan-warning-unset': original(False),
    'boolnot-reference-nan-warning-supplied-throw': original(True),
}
