"""Failed += conversion reports the old selected pair after both names rebind."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $ok = $GLOBALS['leftAlias'] === '12.5tail' && $GLOBALS['rightAlias'] === 2;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ':', $ok, ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered' || $GLOBALS['calls'] !== 1 || !$ok) { echo 'BAD-H;'; return true; }
    $GLOBALS['leftAlias'] = false; $GLOBALS['rightAlias'] = 'bad' . $GLOBALS['digit'];
    $GLOBALS['left'] =& $GLOBALS['replacementLeft'];
    $GLOBALS['right'] =& $GLOBALS['replacementRight']; return false;
}
$tail = 'tail'; $left = '12.5' . $tail; $right = 2; $digit = '5';
$leftAlias =& $left; $rightAlias =& $right;
$replacementLeft = 77; $replacementRight = 7; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = ($left', '        +=', '        $right);',
              "    echo 'BAD-R;';", '} catch (Throwable $e) {',
              "    echo 'E:', $e instanceof TypeError, ':', $e->getMessage() === 'Unsupported operand types: bool + string', ':', $e->getLine(), ':', $e->getPrevious() === null, ':', $v === 100, ':', $calls === 1, ':', $leftAlias === false, ':', $rightAlias === 'bad5', ':', $left === 77, ':', $replacementLeft === 77, ':', $right === 7, ':', $replacementRight === 7, ';';",
              "} finally { echo 'F;'; }", '$leftAlias = 73; $rightAlias = 4;',
              "echo 'A:', $leftAlias === 73, ':', $rightAlias === 4, ':', $left === 77, ':', $right === 7, ':', $v === 100, ';';",
              '$left = 8; $right = 9;',
              "echo 'B:', $left === 8, ':', $replacementLeft === 8, ':', $leftAlias === 73, ':', $right === 9, ':', $replacementRight === 9, ':', $rightAlias === 4, ':', $v === 100, ';END;';"]
    assert lines[22] == '    $v = ($left' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'addassign-selected-failure-rebound-live-types': original()}
