"""Selected-reference subtraction cancels its store on a second conversion throw."""


def original():
    lines = """<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $first = $GLOBALS['calls'] === 1;
    $ok = $first ? ($GLOBALS['leftAlias'] === '12.5tail' && $GLOBALS['rightAlias'] === 2) : ($GLOBALS['leftAlias'] === 99 && $GLOBALS['rightAlias'] === '5.5tail' && $GLOBALS['right'] === 7);
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ':', $ok, ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered' || $GLOBALS['calls'] > 2 || !$ok) { echo 'BAD-H;'; return true; }
    if ($first) { $GLOBALS['leftAlias'] = 99; $GLOBALS['rightAlias'] = '5.5tail'; $GLOBALS['right'] =& $GLOBALS['replacementRight']; return true; }
    $GLOBALS['leftAlias'] = 88; $GLOBALS['rightAlias'] = 7; $GLOBALS['left'] =& $GLOBALS['replacementLeft'];
    throw $GLOBALS['second'];
}
$tail = 'tail'; $left = '12.5' . $tail; $right = 2;
$leftAlias =& $left; $rightAlias =& $right;
$replacementLeft = 77; $replacementRight = 7; $calls = 0; $v = 100;""".splitlines()
    lines += [''] * (19 - len(lines))
    lines += ["$second = new Exception('subassign');", "set_error_handler('h', 2);", 'try {', '    $v = ($left', '        -=', '        $right);',
              "    echo 'BAD-R;';", '} catch (Throwable $e) {',
              "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', $calls === 2, ':', $leftAlias === 88, ':', $left === 77, ':', $rightAlias === 7, ':', $right === 7, ';';",
              "    $leftAlias = 73; echo 'T:', $leftAlias === 73, ':', $left === 77, ':', $v === 100, ';';", "} finally { echo 'F;'; }", '$leftAlias = 6; $rightAlias = 4;',
              "echo 'A:', $leftAlias === 6, ':', $rightAlias === 4, ':', $left === 77, ':', $right === 7, ';';", '$left = 8; $right = 9;',
              "echo 'B:', $left === 8, ':', $replacementLeft === 8, ':', $leftAlias === 6, ':', $right === 9, ':', $replacementRight === 9, ':', $rightAlias === 4, ':', $v === 100, ';END;';"]
    assert lines[19] == "$second = new Exception('subassign');"
    assert lines[22] == '    $v = ($left' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'subassign-warning-second-throw': original()}
