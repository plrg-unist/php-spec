"""NaN bitwise NOT keeps its zero conversion through two diagnostic callbacks."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m, ';';
    if ($GLOBALS['calls'] === 1) { $GLOBALS['x'] = 99; return true; }
    unset($GLOBALS['x']);
    return false;
}
$x = NAN; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 8194);", 'try {', '    $v =', '        ~', '        $x;',
              "    echo 'R:', $v, ':', $v === -1, ':', isset($x) === false, ':', $calls === 2, ';';",
              "} catch (Throwable $e) { echo 'BAD-E:', $e->getLine(), ';';",
              "} finally { echo 'F;'; }",
              "echo 'END:', isset($x) === false, ':', $v === -1, ':', $calls === 2, ';';"]
    assert lines[23] == '        ~' and lines[24] == '        $x;'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'bitnot-nan-retired-default-deprecated': original()}
