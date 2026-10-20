"""Selected += holders survive RHS retirement and target-name rebinding."""


def original():
    before = "($GLOBALS['calls'] === 1 ? ($GLOBALS['leftAlias'] === '12.5tail' && $GLOBALS['rightAlias'] === 2) : ($GLOBALS['leftAlias'] === 99 && $GLOBALS['rightAlias'] === '5.5tail' && $GLOBALS['right'] === 7))"
    lines = f'''<?php
function h($n, $m, $file, $line) {{
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ':', {before}, ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered' || ($GLOBALS['calls'] !== 1 && $GLOBALS['calls'] !== 2)) {{ echo 'BAD-H;'; return true; }}
    if ($GLOBALS['calls'] === 1) {{
        $GLOBALS['leftAlias'] = 99; $GLOBALS['rightAlias'] = '5.5tail';
        $GLOBALS['right'] =& $GLOBALS['replacementRight']; return true;
    }}
    $GLOBALS['leftAlias'] = 88;
    $GLOBALS['left'] =& $GLOBALS['replacementLeft'];
    unset($GLOBALS['rightAlias']); return false;
}}
$tail = 'tail'; $left = '12.5' . $tail; $right = 2;
$leftAlias =& $left; $rightAlias =& $right;
$replacementLeft = 77; $replacementRight = 7; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = ($left', '        +=', '        $right);']
    lines += ["    echo 'R:', $v, ':', $v === 18.0, ':', $leftAlias === 18.0, ':', $left === 77, ':', $replacementLeft === 77, ':', $right === 7, ':', $replacementRight === 7, ':', isset($rightAlias) === false, ':', $calls === 2, ';';",
              "} catch (Throwable $e) { echo 'BAD-E:', $e->getLine(), ';';",
              "} finally { echo 'F;'; }",
              '$leftAlias = 6;',
              "echo 'A:', $leftAlias === 6, ':', $left === 77, ':', $replacementLeft === 77, ':', $right === 7, ':', $v === 18.0, ';';",
              '$left = 8;',
              "echo 'B:', $left === 8, ':', $replacementLeft === 8, ':', $leftAlias === 6, ':', $right === 7, ':', $replacementRight === 7, ':', $v === 18.0, ';END;';"]
    assert lines[22] == '    $v = ($left' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'addassign-selected-rhs-warning-rebound-retired': original()}
