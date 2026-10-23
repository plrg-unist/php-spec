"""A selected float copy survives source removal and condition reversal."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $n, ':', $line, ':', $m, ';';
    $GLOBALS['x'] = 99; unset($GLOBALS['x']);
    $GLOBALS['pick'] = false; return false;
}
$x = 12.5; $pick = true; $other = 29.5; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 8192);", 'try {', '    $v = ~($pick',
              '        ? $x', '        : $other);',
              "    echo 'R:', $v, ':', $v === -13, ':', isset($x) === false, ':', $other === 29.5, ':', $pick === false, ':', $calls === 1, ';';",
              "} catch (Throwable $e) { echo 'BAD-E;';",
              "} finally { echo 'F;'; }", '$x = 8;',
              "echo 'END:', $v === -13, ':', $x === 8, ':', $other === 29.5, ':', $pick === false, ':', $calls === 1, ';';"]
    assert lines[22] == '    $v = ~($pick' and lines[24] == '        : $other);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'bitnot-copy-warning-ternary-snapshot': original()}
