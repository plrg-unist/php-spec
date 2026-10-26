"""OP93 original sources: evaluated range-only floats under bitwise NOT."""

def throwing():
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
$x = INF; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (19 - len(lines))
    lines += ["$second = new Exception('copy-range');", "set_error_handler('h', 2);", 'try {',
              '    $v = (', '        ~', '        copied_value());',
              "    echo 'BAD-R;';", '} catch (Throwable $e) {',
              "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', !isset($x), ':', $calls === 1, ';';",
              "} finally { echo 'F;'; }", '$x = 8;',
              "echo 'END:', $x === 8, ':', $v === 100, ':', $calls === 1, ';';"]
    assert lines[23] == '        ~' and lines[24] == '        copied_value());'
    return ('\n'.join(lines) + '\n').encode()


def selected():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $n, ':', $line, ':', $m, ';';
    $GLOBALS['x'] = 99;
    unset($GLOBALS['x']);
    $GLOBALS['pick'] = false;
    return false;
}
$x = 9223372036854775808.0; $pick = true; $other = 5.5; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = ~($pick',
              '        ? $x', '        : $other);',
              "    echo 'R:', $v, ':', $v === 9223372036854775807, ':', !isset($x), ':', $other === 5.5, ':', $pick === false, ':', $calls === 1, ';';",
              "} catch (Throwable $e) { echo 'BAD-E:', $e->getLine(), ';';",
              "} finally { echo 'F;'; }", '$x = 8;',
              "echo 'END:', $v === 9223372036854775807, ':', $x === 8, ':', $other === 5.5, ':', $pick === false, ':', $calls === 1, ';';"]
    assert lines[22] == '    $v = ~($pick' and lines[24] == '        : $other);'
    return ('\n'.join(lines) + '\n').encode()

CASES = {
    'copy-range-inf-supplied-throw': throwing(),
    'copy-range-wrap-selected': selected(),
}
