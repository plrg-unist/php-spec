"""A NaN LEFT conversion finishes its remaining diagnostic before unwinding."""


def original(mask):
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m, ';';
    $GLOBALS['x'] = 99; $GLOBALS['y'] = 0;
    throw $GLOBALS['second'];
}
$x = NAN; $y = 5; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (19 - len(lines))
    lines += ["$second = new Exception('mod-nan-pending');", f"set_error_handler('h', {mask});", 'try {', '    $v = ($x', '        %', '        $y);',
              "    echo 'BAD-R;';", '} catch (Throwable $e) {',
              "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', $x === 99, ':', $y === 0, ':', $calls === 1, ';';",
              "} finally { echo 'F;'; }", '$x = 8; $y = 9;',
              "echo 'END:', $x === 8, ':', $y === 9, ':', $v === 100, ':', $calls === 1, ';';"]
    assert lines[19] == "$second = new Exception('mod-nan-pending');"
    assert lines[23] == '        %' and lines[24] == '        $y);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'mod-nan-pending-ineligible-precision': original(2),
    'mod-nan-pending-eligible-precision': original(8194),
}
