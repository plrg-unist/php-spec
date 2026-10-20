"""A completed by-value float producer precedes BITNOT's throwing Deprecated."""


def original():
    lines = '''<?php
function copied_value() {
    echo 'P;';
    return $GLOBALS['x'];
}
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $n, ':', $line, ':', $m, ';';
    $GLOBALS['x'] = 99;
    unset($GLOBALS['x']);
    throw $GLOBALS['second'];
}
$x = 12.5; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (19 - len(lines))
    lines += ["$second = new Exception('bitnot-copy');", "set_error_handler('h', 8192);", 'try {', '    $v = (', '        ~', '        copied_value());',
              "    echo 'BAD-R;';", '} catch (Throwable $e) {',
              "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', !isset($x), ':', $calls === 1, ';';",
              "} finally { echo 'F;'; }", '$x = 8;',
              "echo 'END:', $x === 8, ':', $v === 100, ':', $calls === 1, ';';"]
    assert lines[19] == "$second = new Exception('bitnot-copy');"
    assert lines[23] == '        ~' and lines[24] == '        copied_value());'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'bitnot-copy-warning-return-throw': original()}
