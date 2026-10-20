"""Cached-zero /= fails after its selected RHS cell is retired by the Warning."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $first = $GLOBALS['calls'] === 1;
    $ok = $first ? ($GLOBALS['leftAlias'] === '12.5tail' && $GLOBALS['rightAlias'] === 2) : ($GLOBALS['leftAlias'] === 99 && $GLOBALS['rightAlias'] === '0tail' && $GLOBALS['right'] === 7);
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ':', $ok, ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered' || $GLOBALS['calls'] > 2 || !$ok) { echo 'BAD-H;'; return true; }
    if ($first) {
        $GLOBALS['leftAlias'] = 99; $GLOBALS['rightAlias'] = '0tail';
        $GLOBALS['right'] =& $GLOBALS['replacementRight']; return true;
    }
    $GLOBALS['leftAlias'] = 88; $GLOBALS['rightAlias'] = 7;
    $GLOBALS['left'] =& $GLOBALS['replacementLeft'];
    unset($GLOBALS['rightAlias']); return false;
}
$tail = 'tail'; $left = '12.5' . $tail; $right = 2;
$leftAlias =& $left; $rightAlias =& $right;
$replacementLeft = 77; $replacementRight = 7; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = ($left', '        /=', '        $right);',
              "    echo 'BAD-R;';",
              "} catch (Throwable $e) {",
              "    echo 'E:', $e instanceof DivisionByZeroError, ':', $e->getMessage() === 'Division by zero', ':', $e->getLine(), ':', $e->getPrevious() === null, ':', $v === 100, ':', $calls === 2, ':', $leftAlias === 88, ':', $left === 77, ':', $replacementLeft === 77, ':', $right === 7, ':', $replacementRight === 7, ':', isset($rightAlias) === false, ';';",
              "} finally { echo 'F;'; }",
              '$leftAlias = 6;',
              "echo 'A:', $leftAlias === 6, ':', $left === 77, ':', $replacementLeft === 77, ':', $right === 7, ':', $v === 100, ';';",
              '$left = 8; $right = 9;',
              "echo 'B:', $left === 8, ':', $replacementLeft === 8, ':', $leftAlias === 6, ':', $right === 9, ':', $replacementRight === 9, ':', isset($rightAlias) === false, ':', $v === 100, ';END;';"]
    assert lines[22] == '    $v = ($left' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'divassign-warning-retired-cached-zero': original()}
