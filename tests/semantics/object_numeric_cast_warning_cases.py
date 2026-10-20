"""A borrowed stdClass numeric cast retires its source before a supplied throw."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m, ';';
    $GLOBALS['x'] = 99;
    echo 'W:', $GLOBALS['weak']->get() === null, ';';
    throw $GLOBALS['second'];
}
$x = new stdClass;
$weak = WeakReference::create($x);
$calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (19 - len(lines))
    lines += ["$second = new Exception('object-numeric-cast');", "set_error_handler('h', 2);", 'try {', '    $v =', '        (int)', '        $x;',
              "    echo 'BAD-R;';", '} catch (Throwable $e) {',
              "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', $x === 99, ':', $calls === 1, ';';",
              "} finally { echo 'F;'; }", '$x = 8;',
              "echo 'END:', $x === 8, ':', $v === 100, ':', $calls === 1, ';';"]
    assert lines[19] == "$second = new Exception('object-numeric-cast');"
    assert lines[23] == '        (int)' and lines[24] == '        $x;'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'object-numeric-cast-warning-int-throw': original()}
