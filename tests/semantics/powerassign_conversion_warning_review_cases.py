"""Converted negative-zero power stores after selected RHS retirement."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $c = $GLOBALS['calls'];
    echo 'H:', $c, ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered' || $m === 'Power of base 0 and negative exponent is deprecated', ';';
    if ($c === 1) { $GLOBALS['leftAlias'] = 99; $GLOBALS['rightAlias'] = '-3tail'; $GLOBALS['right'] =& $GLOBALS['replacementRight']; return true; }
    if ($c === 2) { $GLOBALS['leftAlias'] = 88; $GLOBALS['rightAlias'] = 7; $GLOBALS['left'] =& $GLOBALS['replacementLeft']; unset($GLOBALS['rightAlias']); return true; }
    $GLOBALS['leftAlias'] = 66; return false;
}
$tail = 'tail'; $left = '-0.0' . $tail; $right = 2;
$leftAlias =& $left; $rightAlias =& $right;
$replacementLeft = 77; $replacementRight = 7; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 8194);", 'try {', '    $v = ($left', '        **=', '        $right);',
              "    echo 'R:', $v, ':', $v === -INF, ':', $leftAlias === -INF, ':', $left === 77, ':', $right === 7, ':', isset($rightAlias) === false, ':', $calls === 3, ';';",
              "} catch (Throwable $e) { echo 'BAD-E:', $e->getLine(), ';';",
              "} finally { echo 'F;'; }", '$leftAlias = 6; $left = 8; $right = 9;',
              "echo 'END:', $leftAlias === 6, ':', $replacementLeft === 8, ':', $replacementRight === 9, ':', isset($rightAlias) === false, ':', $v === -INF, ';';"]
    assert lines[22] == '    $v = ($left' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'powerassign-conversion-warning-negative-retired': original()}
