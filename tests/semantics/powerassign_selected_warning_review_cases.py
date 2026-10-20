"""Selected **= preserves signed captured operands after RHS retirement."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $ok = $GLOBALS['leftAlias'] === -0.0 && $GLOBALS['rightAlias'] === -3;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'Power of base 0 and negative exponent is deprecated', ':', $ok, ';';
    if ($n !== 8192 || $line !== 25 || $m !== 'Power of base 0 and negative exponent is deprecated' || $GLOBALS['calls'] !== 1 || !$ok) { echo 'BAD-H;'; return true; }
    $GLOBALS['leftAlias'] = 88; $GLOBALS['rightAlias'] = 7;
    $GLOBALS['left'] =& $GLOBALS['replacementLeft'];
    $GLOBALS['right'] =& $GLOBALS['replacementRight'];
    unset($GLOBALS['rightAlias']); return false;
}
$left = -0.0; $right = -3;
$leftAlias =& $left; $rightAlias =& $right;
$replacementLeft = 77; $replacementRight = 7; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 8192);", 'try {', '    $v = ($left', '        **=', '        $right);',
              "    echo 'R:', $v, ':', $v === -1e999, ':', $leftAlias === -1e999, ':', $left === 77, ':', $replacementLeft === 77, ':', $right === 7, ':', $replacementRight === 7, ':', isset($rightAlias) === false, ':', $calls === 1, ';';",
              "} catch (Throwable $e) { echo 'BAD-E:', $e->getLine(), ';';",
              "} finally { echo 'F;'; }",
              '$leftAlias = 6;',
              "echo 'A:', $leftAlias === 6, ':', $left === 77, ':', $replacementLeft === 77, ':', $right === 7, ':', $v === -1e999, ';';",
              '$left = 8; $right = 9;',
              "echo 'B:', $left === 8, ':', $replacementLeft === 8, ':', $leftAlias === 6, ':', $right === 9, ':', $replacementRight === 9, ':', isset($rightAlias) === false, ':', $v === -1e999, ';END;';"]
    assert lines[22] == '    $v = ($left' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'powerassign-selected-warning-negative-retired': original()}
