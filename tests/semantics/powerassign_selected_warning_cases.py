"""Selected-reference power assignment commits its saved result before handler throw."""


def original():
    lines = """<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $ok = $GLOBALS['calls'] === 1 && $GLOBALS['leftAlias'] === 0 && $GLOBALS['rightAlias'] === -2;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'Power of base 0 and negative exponent is deprecated', ':', $ok, ';';
    if ($n !== 8192 || $line !== 25 || $m !== 'Power of base 0 and negative exponent is deprecated' || !$ok) { echo 'BAD-H;'; return true; }
    $GLOBALS['leftAlias'] = 88; $GLOBALS['rightAlias'] = 7;
    $GLOBALS['left'] =& $GLOBALS['replacementLeft']; $GLOBALS['right'] =& $GLOBALS['replacementRight'];
    throw $GLOBALS['second'];
}
$left = 0; $right = -2;
$leftAlias =& $left; $rightAlias =& $right;
$replacementLeft = 77; $replacementRight = 7; $calls = 0; $v = 100;""".splitlines()
    lines += [''] * (19 - len(lines))
    lines += ["$second = new Exception('powerassign-selected');", "set_error_handler('h', 8192);", 'try {', '    $v = ($left', '        **=', '        $right);',
              "    echo 'BAD-R;';", '} catch (Throwable $e) {',
              "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', $calls === 1, ':', $leftAlias === 1e999, ':', $left === 77, ':', $replacementLeft === 77, ':', $rightAlias === 7, ':', $right === 7, ':', $replacementRight === 7, ';';",
              "    $leftAlias = 73; echo 'T:', $leftAlias === 73, ':', $left === 77, ':', $v === 100, ';';", "} finally { echo 'F;'; }", '$leftAlias = 6; $rightAlias = 4;',
              "echo 'A:', $leftAlias === 6, ':', $rightAlias === 4, ':', $left === 77, ':', $right === 7, ';';", '$left = 8; $right = 9;',
              "echo 'B:', $left === 8, ':', $replacementLeft === 8, ':', $leftAlias === 6, ':', $right === 9, ':', $replacementRight === 9, ':', $rightAlias === 4, ':', $v === 100, ';END;';"]
    assert lines[19] == "$second = new Exception('powerassign-selected');"
    assert lines[22] == '    $v = ($left' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'powerassign-selected-warning-pending-throw': original()}
