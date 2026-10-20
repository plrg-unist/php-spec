"""Selected XOR protects fractional text after the old RHS cell retires."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m, ';';
    if ($GLOBALS['calls'] === 1) {
        $GLOBALS['leftAlias'] = 99; $GLOBALS['rightAlias'] = '5.5tail';
        $GLOBALS['right'] =& $GLOBALS['replacementRight']; return true;
    }
    if ($GLOBALS['calls'] === 2) {
        $GLOBALS['leftAlias'] = 88; $GLOBALS['left'] =& $GLOBALS['replacementLeft'];
        $GLOBALS['rightAlias'] = 7; unset($GLOBALS['rightAlias']); return true;
    }
    $GLOBALS['leftAlias'] = 66; return false;
}
$left = 12.5; $right = 2;
$leftAlias =& $left; $rightAlias =& $right;
$replacementLeft = 77; $replacementRight = 7; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 8194);", 'try {', '    $v = ($left', '        ^=', '        $right);',
              "    echo 'R:', $v, ':', $v === 9, ':', $leftAlias === 9, ':', $left === 77, ':', $right === 7, ':', isset($rightAlias) === false, ':', $calls === 3, ';';",
              "} catch (Throwable $e) { echo 'BAD-E;';",
              "} finally { echo 'F;'; }", '$leftAlias = 6; $left = 8; $right = 9;',
              "echo 'END:', $leftAlias === 6, ':', $replacementLeft === 8, ':', $replacementRight === 9, ':', isset($rightAlias) === false, ':', $v === 9, ':', $calls === 3, ';';"]
    assert lines[22] == '    $v = ($left' and lines[23] == '        ^=' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'xorassign-selected-rhs-warning-retired-text': original()}
