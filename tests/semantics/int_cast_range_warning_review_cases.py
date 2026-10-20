"""An explicit NaN cast emits only its range Warning before supplied throw."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $n, ':', $line, ':', $m, ';';
    $GLOBALS['x'] = 99; unset($GLOBALS['x']);
    throw $GLOBALS['second'];
}
$x = NAN; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (19 - len(lines))
    lines += ["$second = new Exception('int-cast-range');", "set_error_handler('h', 2);", 'try {', '    $v = (', '        (int)', '        $x);',
              "    echo 'BAD-R;';", '} catch (Throwable $e) {',
              "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', isset($x) === false, ':', $calls === 1, ';';",
              "} finally { echo 'F;'; }", '$x = 8;',
              "echo 'END:', $x === 8, ':', $v === 100, ':', $calls === 1, ';';"]
    assert lines[19] == "$second = new Exception('int-cast-range');"
    assert lines[23] == '        (int)' and lines[24] == '        $x);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'int-cast-range-nan-warning-throw': original()}
