"""Selected compound ADD delays a nonnumeric RHS until after LEFT Warning."""


def original():
    lines = """<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":", ($m === 'A non-numeric value encountered'), ";";
    if ($GLOBALS['calls'] === 1) {
        $GLOBALS['leftAlias'] = 99; $GLOBALS['rightAlias'] = '5.5tail';
        $GLOBALS['right'] =& $GLOBALS['replacementRight'];
        return true;
    }
    $GLOBALS['leftAlias'] = 88; $GLOBALS['rightAlias'] = 7;
    $GLOBALS['left'] =& $GLOBALS['replacementLeft'];
    throw $GLOBALS['supplied'];
}
$tail = 'tail'; $left = '12.5' . $tail; $right = 'bad' . 5;
$leftAlias =& $left; $rightAlias =& $right;
$replacementLeft = 77; $replacementRight = 7; $calls = 0; $v = 100;""".splitlines()
    lines += [''] * (19 - len(lines))
    lines += ['$supplied = new Exception("supplied");', 'set_error_handler("h", E_WARNING);', 'try {',
              '    $v = ($left', '        +=', '        $right);',
              '    echo "UNEXPECTED;";', '} catch (Throwable $e) {',
              '    echo "C:", ($e === $supplied), ":", ($e->getPrevious() === null), ":", $e->getLine(), ":", ($v === 100), ":", ($leftAlias === 88), ":", ($rightAlias === 7), ":", ($left === 77 && $right === 7), ":", ($calls === 2), ";";',
              '} finally { echo "F;"; }', '$leftAlias = 6; $rightAlias = 4; $left = 8; $right = 9;',
              'echo "END:", ($leftAlias === 6), ":", ($rightAlias === 4), ":", ($replacementLeft === 8), ":", ($replacementRight === 9), ":", ($v === 100), ";";']
    assert lines[19].startswith('$supplied =') and lines[22].startswith('    $v =')
    assert lines[24].strip() == '$right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'addassign-repair-second-throw': original()}
