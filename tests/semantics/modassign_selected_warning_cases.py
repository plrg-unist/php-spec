"""Selected modulo target survives while RHS is dereferenced after Deprecated."""


def original():
    lines = """<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $n, ":", $line, ":", ($m === 'Implicit conversion from float 12.5 to int loses precision'), ";";
    $GLOBALS['leftAlias'] = 99;
    $GLOBALS['right'] =& $GLOBALS['replacementRight'];
    $GLOBALS['left'] =& $GLOBALS['replacementLeft'];
    return true;
}
$left = 12.5; $right = 0;
$leftAlias =& $left; $rightAlias =& $right;
$replacementLeft = 77; $replacementRight = 5; $calls = 0; $v = 100;""".splitlines()
    lines += [''] * (20 - len(lines))
    lines += ['set_error_handler("h", E_DEPRECATED);', 'try {',
              '    $v = ($left', '        %=', '        $right);',
              '    echo "R:", $v, ":", ($v === 2), ":", ($leftAlias === 2), ":", ($rightAlias === 0), ":", ($left === 77 && $right === 5), ":", ($calls === 1), ";";',
              '} catch (Throwable $e) { echo "BAD-E:", $e->getLine(), ";";',
              '} finally { echo "F;"; }', '$leftAlias = 6; $rightAlias = 4; $left = 8; $right = 9;',
              'echo "END:", ($leftAlias === 6), ":", ($rightAlias === 4), ":", ($replacementLeft === 8), ":", ($replacementRight === 9), ":", ($v === 2), ";";']
    assert lines[22].startswith('    $v =') and lines[24].strip() == '$right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'modassign-selected-warning-rebound-right': original()}
