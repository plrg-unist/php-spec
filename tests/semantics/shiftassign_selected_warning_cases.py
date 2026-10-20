"""A delayed current negative shift count prevents selected-target storage."""


def original():
    lines = """<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m, ';';
    $GLOBALS['leftAlias'] = 88;
    $GLOBALS['right'] =& $GLOBALS['replacementRight'];
    $GLOBALS['left'] =& $GLOBALS['replacementLeft'];
    return true;
}
$left = -12.5; $right = 2;
$leftAlias =& $left; $rightAlias =& $right;
$replacementLeft = 77; $replacementRight = -1; $calls = 0; $v = 100;""".splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 8192);", 'try {', '    $v = ($left', '        >>=', '        $right);',
              "    echo 'BAD-R;';",
              "} catch (Throwable $e) { echo 'E:', ($e instanceof ArithmeticError), ':', ($e->getMessage() === 'Bit shift by negative number'), ':', $e->getLine(), ':', ($e->getPrevious() === null), ':', ($v === 100), ':', ($leftAlias === 88), ':', ($left === 77), ':', ($rightAlias === 2), ':', ($right === -1), ':', ($calls === 1), ';';",
              "} finally { echo 'F;'; }", '$leftAlias = 6; $rightAlias = 4; $left = 8; $right = 9;',
              "echo 'END:', ($leftAlias === 6), ':', ($rightAlias === 4), ':', ($replacementLeft === 8), ':', ($replacementRight === 9), ':', ($v === 100), ';';"]
    assert lines[22].startswith('    $v =') and lines[23].strip() == '>>=' and lines[24].strip() == '$right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'shiftassign-selected-warning-negative-count': original()}
