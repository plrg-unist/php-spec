"""Delayed ADD rejection and quiet repair of the selected old RHS."""


def original(rebound):
    initial = "($GLOBALS['left'] === '12tail' && $GLOBALS['right'] === 'bad5')"
    lines = f'''<?php
function h($n, $m, $file, $line) {{
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ':', {initial}, ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered' || $GLOBALS['calls'] !== 1) {{ echo 'BAD-H;'; return true; }}'''.splitlines()
    if rebound:
        lines += [
            "    $GLOBALS['left'] = 99; $GLOBALS['rightAlias'] = '5.5';",
            "    $GLOBALS['right'] =& $GLOBALS['replacement']; return false;",
        ]
    else:
        lines += ["    $GLOBALS['left'] = false; return false;"]
    lines += ['}', '$calls = 0; $tail = 5;',
              "$left = '12tail'; $leftAlias =& $left;",
              "$right = 'bad' . $tail; $rightAlias =& $right;",
              "$replacement = '2tail'; $v = 100;" if rebound else '$v = 100;']
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = ($left', '        +', '        $right);']
    if rebound:
        lines += ["    echo 'R:', $v, ':', $v === 17.5, ':', $left === 99, ':', $leftAlias === 99, ':', $right === '2tail', ':', $replacement === '2tail', ':', $rightAlias === '5.5', ':', $calls === 1, ';';",
                  "} catch (Throwable $e) { echo 'BAD-E:', $e->getLine(), ';';"]
    else:
        lines += ["    echo 'BAD-R;';", '} catch (Throwable $e) {',
                  "    echo 'E:', $e instanceof TypeError, ':', $e->getMessage() === 'Unsupported operand types: bool + string', ':', $e->getLine(), ':', $e->getPrevious() === null, ':', $v === 100, ':', $left === false, ':', $leftAlias === false, ':', $right === 'bad5', ':', $rightAlias === 'bad5', ':', $calls === 1, ';';"]
    lines += ["} finally { echo 'F;'; }"]
    if rebound:
        lines += ["$rightAlias = 6; $left = 7;",
                  "echo 'A:', $leftAlias === 7, ':', $rightAlias === 6, ':', $right === '2tail', ':', $replacement === '2tail', ';';",
                  '$right = 8;', "echo 'B:', $replacement === 8, ':', $rightAlias === 6, ';END;';"]
    else:
        lines += ['$left = 7; $right = 8;', "echo 'A:', $leftAlias === 7, ':', $rightAlias === 8, ';END;';"]
    assert lines[22] == '    $v = ($left' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'add-repair-unrepaired-live-types': original(False),
    'add-repair-old-right-quiet-float': original(True),
}
