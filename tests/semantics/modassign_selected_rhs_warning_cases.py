"""Second RHS Deprecated cannot repair the already captured modulo zero."""


def original():
    lines = """<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m, ';';
    if ($GLOBALS['calls'] === 1) { $GLOBALS['leftAlias'] = 99; $GLOBALS['right'] =& $GLOBALS['replacementRight']; return true; }
    $GLOBALS['leftAlias'] = 88;
    $GLOBALS['left'] =& $GLOBALS['replacementLeft'];
    $GLOBALS['replacementRight'] = 5;
    return true;
}
$left = 12.5; $right = 5;
$leftAlias =& $left; $rightAlias =& $right;
$replacementLeft = 77; $replacementRight = 0.5; $calls = 0; $v = 100;""".splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 8192);", 'try {', '    $v = ($left', '        %=', '        $right);',
              "    echo 'BAD-R;';",
              "} catch (Throwable $e) { echo 'E:', ($e instanceof DivisionByZeroError), ':', ($e->getMessage() === 'Modulo by zero'), ':', $e->getLine(), ':', ($e->getPrevious() === null), ':', ($v === 100), ':', ($leftAlias === 88), ':', ($left === 77), ':', ($rightAlias === 5), ':', ($right === 5), ':', ($calls === 2), ';';",
              "} finally { echo 'F;'; }", '$leftAlias = 6; $rightAlias = 4; $left = 8; $right = 9;',
              "echo 'END:', ($leftAlias === 6), ':', ($rightAlias === 4), ':', ($replacementLeft === 8), ':', ($replacementRight === 9), ':', ($v === 100), ';';"]
    assert lines[22].startswith('    $v =') and lines[23].strip() == '%=' and lines[24].strip() == '$right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'modassign-selected-rhs-warning-cached-zero': original()}
