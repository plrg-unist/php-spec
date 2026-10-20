"""A selected right shift keeps its captured negative sign and reads the rebound count."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $n, ':', $line, ':', $m, ';';
    $GLOBALS['leftAlias'] = 99;
    $GLOBALS['right'] =& $GLOBALS['replacementRight'];
    $GLOBALS['left'] =& $GLOBALS['replacementLeft'];
    return false;
}
$left = -12.5; $right = 2;
$leftAlias =& $left; $rightAlias =& $right;
$replacementLeft = 77; $replacementRight = 64; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 8192);", 'try {', '    $v = ($left', '        >>=', '        $right);',
              "    echo 'R:', $v, ':', $v === -1, ':', $leftAlias === -1, ':', $rightAlias === 2, ':', $left === 77, ':', $right === 64, ':', $calls === 1, ';';",
              "} catch (Throwable $e) { echo 'BAD-E;';",
              "} finally { echo 'F;'; }", '$leftAlias = 6; $rightAlias = 4; $left = 8; $right = 9;',
              "echo 'END:', $leftAlias === 6, ':', $rightAlias === 4, ':', $replacementLeft === 8, ':', $replacementRight === 9, ':', $v === -1, ':', $calls === 1, ';';"]
    assert lines[22] == '    $v = ($left' and lines[23] == '        >>=' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'shiftassign-selected-warning-saturated-sign': original()}
