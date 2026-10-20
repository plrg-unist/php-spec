"""Modulo assignment reads the rebound RHS after converting its old target."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $n, ':', $line, ':', $m === 'Implicit conversion from float 12.5 to int loses precision', ';';
    $GLOBALS['leftAlias'] = 88;
    $GLOBALS['right'] =& $GLOBALS['replacementRight'];
    $GLOBALS['left'] =& $GLOBALS['replacementLeft'];
    return false;
}
$left = 12.5; $right = 5;
$leftAlias =& $left; $rightAlias =& $right;
$replacementLeft = 77; $replacementRight = 0; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 8192);", 'try {', '    $v = ($left', '        %=', '        $right);',
              "    echo 'BAD-R;';",
              "} catch (Throwable $e) { echo 'E:', $e instanceof DivisionByZeroError, ':', $e->getMessage() === 'Modulo by zero', ':', $e->getLine(), ':', $e->getPrevious() === null, ':', $v === 100, ':', $leftAlias === 88, ':', $rightAlias === 5, ':', $left === 77, ':', $right === 0, ':', $calls === 1, ';';",
              "} finally { echo 'F;'; }", '$leftAlias = 6; $rightAlias = 4; $left = 8; $right = 9;',
              "echo 'END:', $leftAlias === 6, ':', $rightAlias === 4, ':', $replacementLeft === 8, ':', $replacementRight === 9, ':', $v === 100, ':', $calls === 1, ';';"]
    assert lines[22] == '    $v = ($left' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'modassign-selected-warning-rebound-zero': original()}
