"""OP92 original sources: evaluated NaN copies under bitwise NOT."""

def throwing(mask):
    lines = '''<?php
function copied_value() {
    echo 'P;';
    return $GLOBALS['x'];
}
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m, ';';
    $GLOBALS['x'] = 99;
    unset($GLOBALS['x']);
    throw $GLOBALS['second'];
}
$x = NAN; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (19 - len(lines))
    lines += ["$second = new Exception('copy-nan');", "set_error_handler('h', " + str(mask) + ");", 'try {',
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
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m, ';';
    if ($GLOBALS['calls'] === 1) {
        $GLOBALS['x'] = 99;
        $GLOBALS['pick'] = false;
        return true;
    }
    unset($GLOBALS['x']);
    return false;
}
$x = NAN; $pick = true; $other = 29.5; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 8194);", 'try {', '    $v = ~($pick',
              '        ? $x', '        : $other);',
              "    echo 'R:', $v, ':', $v === -1, ':', !isset($x), ':', $other === 29.5, ':', $pick === false, ':', $calls === 2, ';';",
              "} catch (Throwable $e) { echo 'BAD-E:', $e->getLine(), ';';",
              "} finally { echo 'F;'; }", '$x = 8;',
              "echo 'END:', $v === -1, ':', $x === 8, ':', $other === 29.5, ':', $pick === false, ':', $calls === 2, ';';"]
    assert lines[22] == '    $v = ~($pick' and lines[24] == '        : $other);'
    return ('\n'.join(lines) + '\n').encode()

CASES = {
    'copy-nan-pending-ineligible-precision': throwing(2),
    'copy-nan-pending-eligible-precision': throwing(8194),
    'copy-nan-selected-two-notices': selected(),
}
