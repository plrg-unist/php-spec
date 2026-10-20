"""Selected XOR keeps the old RHS referent after its current name is rebound."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $n, ':', $line, ':', $m, ';';
    $GLOBALS['leftAlias'] = 99;
    $GLOBALS['rightAlias'] = 5;
    $GLOBALS['right'] =& $GLOBALS['replacementRight'];
    $GLOBALS['left'] =& $GLOBALS['replacementLeft'];
    return false;
}
$left = 12.5; $right = 2;
$leftAlias =& $left; $rightAlias =& $right;
$replacementLeft = 77; $replacementRight = 7; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 8192);", 'try {', '    $v = ($left', '        ^=', '        $right);',
              "    echo 'R:', $v, ':', $v === 9, ':', $leftAlias === 9, ':', $rightAlias === 5, ':', $left === 77, ':', $right === 7, ':', $calls === 1, ';';",
              "} catch (Throwable $e) { echo 'BAD-E;';",
              "} finally { echo 'F;'; }", '$leftAlias = 6; $rightAlias = 4; $left = 8; $right = 9;',
              "echo 'END:', $leftAlias === 6, ':', $rightAlias === 4, ':', $replacementLeft === 8, ':', $replacementRight === 9, ':', $v === 9, ':', $calls === 1, ';';"]
    assert lines[22] == '    $v = ($left' and lines[23] == '        ^=' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'xorassign-selected-warning-old-rhs': original()}
