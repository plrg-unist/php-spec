"""A selected ternary copy survives source removal and keeps unary zero sign."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $n, ':', $line, ':', $m, ';';
    $GLOBALS['source'] = 99; unset($GLOBALS['source']);
    $GLOBALS['pick'] = false; return false;
}
$tail = 'tail'; $source = '0.0' . $tail;
$pick = true; $other = 7; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = -($pick', '        ? $source', "        : ($other = 'bad'));",
              "    echo 'R:', $v, ':', $v === 0.0, ':', isset($source) === false, ':', $other === 7, ':', $pick === false, ':', $calls === 1, ';';",
              "} catch (Throwable $e) { echo 'BAD-E;';",
              "} finally { echo 'F;'; }", '$other = 8;',
              "echo 'END:', $v === 0.0, ':', isset($source) === false, ':', $other === 8, ':', $pick === false, ':', $calls === 1, ';';"]
    assert lines[22] == '    $v = -($pick' and lines[24] == "        : ($other = 'bad'));"
    return ('\n'.join(lines) + '\n').encode()


CASES = {'unary-copy-warning-ternary-negative-zero': original()}
