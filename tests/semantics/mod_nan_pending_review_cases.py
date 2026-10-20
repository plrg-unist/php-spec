"""Modulo reads the divisor after both NaN conversion diagnostics finish."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m, ';';
    if ($GLOBALS['calls'] === 1) { $GLOBALS['x'] = 99; $GLOBALS['y'] = 0; return true; }
    $GLOBALS['x'] = 88; $GLOBALS['y'] = 5; return false;
}
$x = NAN; $y = 0; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 8194);", 'try {', '    $v = ($x', '        %', '        $y);',
              "    echo 'R:', $v, ':', $v === 0, ':', $x === 88, ':', $y === 5, ':', $calls === 2, ';';",
              "} catch (Throwable $e) { echo 'BAD-E;';",
              "} finally { echo 'F;'; }", '$x = 8; $y = 9;',
              "echo 'END:', $v === 0, ':', $x === 8, ':', $y === 9, ':', $calls === 2, ';';"]
    assert lines[22] == '    $v = ($x' and lines[23] == '        %' and lines[24] == '        $y);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'mod-nan-left-current-right': original()}
