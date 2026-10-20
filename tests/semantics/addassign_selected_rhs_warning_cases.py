"""A second += Warning throw cancels storage through a selected reference."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $ok = $GLOBALS['calls'] === 1 ? ($GLOBALS['left'] === '12.5tail' && $GLOBALS['right'] === 2) : ($GLOBALS['calls'] === 2 && $GLOBALS['left'] === 99 && $GLOBALS['right'] === '5.5tail');
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ':', $ok, ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered' || !$ok) { echo 'BAD-H;'; return true; }
    if ($GLOBALS['calls'] === 1) { $GLOBALS['left'] = 99; $GLOBALS['right'] = '5.5tail'; return true; }
    $GLOBALS['left'] = 88; $GLOBALS['right'] = 7;
    throw $GLOBALS['second'];
}
$tail = 'tail'; $left = '12.5' . $tail; $right = 2;
$leftAlias =& $left; $rightAlias =& $right;
$calls = 0; $v = 100;'''.splitlines()
    assert len(lines) <= 19
    lines += [''] * (19 - len(lines))
    lines += ["$second = new Exception('second');", "set_error_handler('h', 2);", 'try {',
              '    $v = ($left', '        +=', '        $right);', "    echo 'BAD-R;';", '} catch (Throwable $e) {',
              "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', $calls === 2, ':', $left === 88, ':', $leftAlias === 88, ':', $right === 7, ':', $rightAlias === 7, ';';",
              "    $leftAlias = 73; echo 'B:', $left === 73, ':', $leftAlias === 73, ':', $v === 100, ';';",
              "} finally { echo 'F;'; }", '$left = 7; $right = 8;',
              "echo 'A:', $leftAlias === 7, ':', $rightAlias === 8, ':', $v === 100, ';END;';"]
    assert lines[19] == "$second = new Exception('second');"
    assert lines[22] == '    $v = ($left' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'addassign-selected-rhs-warning-second-throw': original()}
