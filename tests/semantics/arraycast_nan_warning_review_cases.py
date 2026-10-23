"""A supplied NaN array-cast handler Exception cancels outer assignment."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $n, ':', $line, ':', $m, ';';
    $GLOBALS['x'] = 0.0;
    throw $GLOBALS['second'];
}
$x = NAN; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (19 - len(lines))
    lines += ["$second = new Exception('arraycast-nan');", "set_error_handler('h', 2);", 'try {',
              '    $v = (', '        (array)', '        $x);',
              "    echo 'BAD-R;';", '} catch (Throwable $e) {',
              "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', $x === 0.0, ':', $calls === 1, ';';",
              "} finally { echo 'F;'; }", '$x = 8;',
              "echo 'END:', $x === 8, ':', $v === 100, ':', $calls === 1, ';';"]
    assert lines[19] == "$second = new Exception('arraycast-nan');"
    assert lines[23] == '        (array)' and lines[24] == '        $x);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'arraycast-nan-warning-supplied-throw': original()}
