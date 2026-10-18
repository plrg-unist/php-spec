"""Delayed DIV rejection and selected-old divisor caching after LEFT Warning."""


def original(zero):
    initial = "($GLOBALS['left'] === '12tail' && $GLOBALS['right'] === 'bad5')"
    if zero:
        initial = "($GLOBALS['calls'] === 1 ? ($GLOBALS['left'] === '12tail' && $GLOBALS['right'] === 'bad5') : ($GLOBALS['left'] === 99 && $GLOBALS['right'] === '2tail' && $GLOBALS['rightAlias'] === '0tail'))"
    lines = f'''<?php
function h($n, $m, $file, $line) {{
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ':', {initial}, ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered') {{ echo 'BAD-H;'; return true; }}'''.splitlines()
    if zero:
        lines += [
            "    if ($GLOBALS['calls'] === 1) {",
            "        $GLOBALS['left'] = 99; $GLOBALS['rightAlias'] = '0tail';",
            "        $GLOBALS['right'] =& $GLOBALS['replacement']; return true;",
            "    }",
            "    $GLOBALS['left'] = 88; $GLOBALS['rightAlias'] = 7; return false;",
        ]
    else:
        lines += ["    $GLOBALS['left'] = false; return false;"]
    lines += ['}', '$calls = 0; $tail = 5;',
              "$left = '12tail'; $leftAlias =& $left;",
              "$right = 'bad' . $tail; $rightAlias =& $right;",
              "$replacement = '2tail'; $v = 100;" if zero else '$v = 100;']
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = ($left', '        /', '        $right);',
              "    echo 'BAD-R;';", '} catch (Throwable $e) {']
    if zero:
        lines += ["    echo 'E:', $e instanceof DivisionByZeroError, ':', $e->getMessage() === 'Division by zero', ':', $e->getLine(), ':', $e->getPrevious() === null, ':', $v === 100, ':', $left === 88, ':', $leftAlias === 88, ':', $right === '2tail', ':', $replacement === '2tail', ':', $rightAlias === 7, ':', $calls === 2, ';';"]
    else:
        lines += ["    echo 'E:', $e instanceof TypeError, ':', $e->getMessage() === 'Unsupported operand types: bool / string', ':', $e->getLine(), ':', $e->getPrevious() === null, ':', $v === 100, ':', $left === false, ':', $leftAlias === false, ':', $right === 'bad5', ':', $rightAlias === 'bad5', ':', $calls === 1, ';';"]
    lines += ["} finally { echo 'F;'; }"]
    if zero:
        lines += ["$rightAlias = 6; $left = 7;",
                  "echo 'A:', $leftAlias === 7, ':', $rightAlias === 6, ':', $right === '2tail', ':', $replacement === '2tail', ';';",
                  '$right = 8;', "echo 'B:', $replacement === 8, ':', $rightAlias === 6, ';END;';"]
    else:
        lines += ['$left = 7; $right = 8;', "echo 'A:', $leftAlias === 7, ':', $rightAlias === 8, ';END;';"]
    assert lines[22] == '    $v = ($left' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'div-repair-unrepaired-live-types': original(False),
    'div-repair-old-right-cached-zero': original(True),
}
