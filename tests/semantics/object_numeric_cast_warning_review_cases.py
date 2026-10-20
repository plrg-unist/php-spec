"""A borrowed stdClass CV retires inside its numeric-cast Warning callback."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $n, ':', $line, ':', $m, ';';
    $GLOBALS['x'] = 99; unset($GLOBALS['x']);
    echo 'W:', $GLOBALS['weak']->get() === null, ':', isset($GLOBALS['x']) === false, ';';
    return false;
}
$x = new stdClass(); $weak = WeakReference::create($x); $calls = 0; $v = 100;
echo 'B:', $weak->get() === $x, ';';'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = (', '        (float)', '        $x);',
              "    echo 'R:', $v, ':', $v === 1.0, ':', isset($x) === false, ':', $calls === 1, ';';",
              "} catch (Throwable $e) { echo 'BAD-E;';",
              "} finally { echo 'F;'; }", '$x = 8;',
              "echo 'END:', $v === 1.0, ':', $x === 8, ':', $calls === 1, ';';"]
    assert lines[23] == '        (float)' and lines[24] == '        $x);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'object-numeric-cast-float-retired': original()}
