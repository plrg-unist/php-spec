"""Selected modulo caches a rebound divisor before its last owner retires."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m, ';';
    if ($GLOBALS['calls'] === 1) {
        $GLOBALS['leftAlias'] = 99;
        $GLOBALS['right'] =& $GLOBALS['replacementRight']; return true;
    }
    $GLOBALS['leftAlias'] = 88;
    $GLOBALS['left'] =& $GLOBALS['replacementLeft'];
    $GLOBALS['replacementRight'] = 7;
    unset($GLOBALS['right'], $GLOBALS['replacementRight']); return false;
}
$left = 12.5; $right = 0;
$leftAlias =& $left; $rightAlias =& $right;
$replacementLeft = 77; $replacementRight = 5.5; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 8192);", 'try {', '    $v = ($left', '        %=', '        $right);',
              "    echo 'R:', $v, ':', $v === 2, ':', $leftAlias === 2, ':', $left === 77, ':', $rightAlias === 0, ':', isset($right) === false, ':', isset($replacementRight) === false, ':', $calls === 2, ';';",
              "} catch (Throwable $e) { echo 'BAD-E:', $e->getLine(), ';';",
              "} finally { echo 'F;'; }", '$leftAlias = 6; $rightAlias = 4; $left = 8;',
              "echo 'END:', $leftAlias === 6, ':', $rightAlias === 4, ':', $replacementLeft === 8, ':', $v === 2, ':', $calls === 2, ':', isset($right) === false, ':', isset($replacementRight) === false, ';';"]
    assert lines[22] == '    $v = ($left' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'modassign-selected-rhs-warning-retired-divisor': original()}
