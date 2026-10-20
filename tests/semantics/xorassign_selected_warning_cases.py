"""Numeric XOR specialization does not retry after selected cells become strings."""


def original():
    lines = """<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m, ';';
    $GLOBALS['leftAlias'] = 'badL';
    $GLOBALS['rightAlias'] = 'badR';
    $GLOBALS['right'] =& $GLOBALS['replacementRight'];
    $GLOBALS['left'] =& $GLOBALS['replacementLeft'];
    return true;
}
$left = 12.5; $right = 2;
$leftAlias =& $left; $rightAlias =& $right;
$replacementLeft = 77; $replacementRight = 7; $calls = 0; $v = 100;""".splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 8192);", 'try {', '    $v = ($left', '        ^=', '        $right);',
              "    echo 'BAD-R;';",
              "} catch (Throwable $e) { echo 'E:', ($e instanceof TypeError), ':', ($e->getMessage() === 'Unsupported operand types: string ^ string'), ':', $e->getLine(), ':', ($e->getPrevious() === null), ':', ($v === 100), ':', ($leftAlias === 'badL'), ':', ($rightAlias === 'badR'), ':', ($left === 77), ':', ($right === 7), ':', ($calls === 1), ';';",
              "} finally { echo 'F;'; }", '$leftAlias = 6; $rightAlias = 4; $left = 8; $right = 9;',
              "echo 'END:', ($leftAlias === 6), ':', ($rightAlias === 4), ':', ($replacementLeft === 8), ':', ($replacementRight === 9), ':', ($v === 100), ';';"]
    assert lines[22].startswith('    $v =') and lines[23].strip() == '^=' and lines[24].strip() == '$right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'xorassign-selected-warning-frozen-numeric-failure': original()}
