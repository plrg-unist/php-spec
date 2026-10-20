"""Delayed += failure preserves a late target alias and reports live types."""


def original():
    initial = "($GLOBALS['left'] === '12.5tail' && $GLOBALS['right'] === 2 && $GLOBALS['alias'] === 0)"
    lines = f'''<?php
function h($n, $m, $file, $line) {{
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ':', {initial}, ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered' || $GLOBALS['calls'] !== 1) {{ echo 'BAD-H;'; return true; }}
    $GLOBALS['alias'] =& $GLOBALS['left'];
    $GLOBALS['left'] = false; $GLOBALS['right'] = 'bad' . $GLOBALS['tail'];
    return false;
}}
$calls = 0; $tail = 5; $alias = 0;
$left = '12.5tail'; $right = 2; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = ($left', '        +=', '        $right);',
              "    echo 'BAD-R;';", '} catch (Throwable $e) {',
              "    echo 'E:', $e instanceof TypeError, ':', $e->getMessage() === 'Unsupported operand types: bool + string', ':', $e->getLine(), ':', $e->getPrevious() === null, ':', $v === 100, ':', $left === false, ':', $alias === false, ':', $right === 'bad5', ':', $calls === 1, ';';",
              '    $alias = 73;', "    echo 'B:', $left === 73, ':', $alias === 73, ':', $v === 100, ';';",
              "} finally { echo 'F;'; }", '$left = 7; $right = 8;',
              "echo 'A:', $left === 7, ':', $alias === 7, ':', $right === 8, ':', $v === 100, ';END;';"]
    assert lines[22] == '    $v = ($left' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'addassign-rhs-failure-live-alias': original()}
