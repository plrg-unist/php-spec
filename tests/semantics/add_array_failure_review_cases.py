"""ADD failure reads the selected old RHS array after its name is rebound."""


def original():
    initial = "($GLOBALS['left'] === '12.5tail' && $GLOBALS['right'] === 2 && $GLOBALS['replacement'] === 7)"
    lines = f'''<?php
function h($n, $m, $file, $line) {{
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ':', {initial}, ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered' || $GLOBALS['calls'] !== 1) {{ echo 'BAD-H;'; return true; }}
    $GLOBALS['leftAlias'] = false; $GLOBALS['rightAlias'] = [2];
    $GLOBALS['right'] =& $GLOBALS['replacement'];
    return false;
}}
$left = '12.5tail'; $leftAlias =& $left;
$right = 2; $rightAlias =& $right;
$replacement = 7; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = ($left', '        +', '        $right);',
              "    echo 'BAD-R;';", '} catch (Throwable $e) {',
              "    echo 'E:', $e instanceof TypeError, ':', $e->getMessage() === 'Unsupported operand types: bool + array', ':', $e->getLine(), ':', $e->getPrevious() === null, ':', $v === 100, ':', $left === false, ':', $leftAlias === false, ':', $right === 7, ':', $replacement === 7, ':', $rightAlias[0] === 2, ':', $calls === 1, ';';",
              "} finally { echo 'F;'; }", '$rightAlias = 3; $left = 7;',
              "echo 'A:', $leftAlias === 7, ':', $rightAlias === 3, ':', $right === 7, ':', $replacement === 7, ':', $v === 100, ';';",
              '$right = 8;', "echo 'B:', $right === 8, ':', $replacement === 8, ':', $rightAlias === 3, ':', $v === 100, ';END;';"]
    assert lines[22] == '    $v = ($left' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'add-array-failure-selected-right-rebind': original()}
