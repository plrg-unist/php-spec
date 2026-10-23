"""Logical XOR caches LEFT truth before a later NaN callback changes it."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m, ';';
    if ($GLOBALS['calls'] === 1) { $GLOBALS['a'] = 1.0; $GLOBALS['b'] = NAN; return true; }
    $GLOBALS['a'] = 0.0; $GLOBALS['b'] = 0.0;
    return false;
}
$a = NAN; $b = 0.0; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = (', '        $a', '        xor $b);',
              "    echo 'R:', $v === true, ':', $a === 0.0, ':', $b === 0.0, ':', $calls === 2, ';';",
              "} catch (Throwable $e) { echo 'BAD-E;'; }", "finally { echo 'F;'; }", '$a = 8; $b = 9;',
              "echo 'END:', $v === true, ':', $a === 8, ':', $b === 9, ':', $calls === 2, ';';"]
    assert len(lines) == 30 and lines[23] == '        $a' and lines[24] == '        xor $b);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'xor-nan-warning-cached-left': original()}
