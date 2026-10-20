"""A supplied leading-text Warning throw skips precision and the compound store."""


def original():
    lines = """<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m, ';';
    if ($GLOBALS['calls'] === 1) { $GLOBALS['leftAlias'] = 99; $GLOBALS['rightAlias'] = '5.5' . $GLOBALS['tail']; $GLOBALS['right'] =& $GLOBALS['replacementRight']; return true; }
    $GLOBALS['leftAlias'] = 88;
    $GLOBALS['rightAlias'] = 7;
    $GLOBALS['left'] =& $GLOBALS['replacementLeft'];
    throw $GLOBALS['second'];
}
$left = 12.5; $right = 2; $tail = 'tail';
$leftAlias =& $left; $rightAlias =& $right;
$replacementLeft = 77; $replacementRight = 7; $calls = 0; $v = 100;""".splitlines()
    lines += [''] * (19 - len(lines))
    lines += ["$second = new Exception('second');", "set_error_handler('h', 8194);", 'try {', '    $v = ($left', '        ^=', '        $right);',
              "    echo 'BAD-R;';",
              "} catch (Throwable $e) { echo 'C:', ($e === $second), ':', ($e->getPrevious() === null), ':', $e->getLine(), ':', ($v === 100), ':', ($leftAlias === 88), ':', ($rightAlias === 7), ':', ($left === 77), ':', ($right === 7), ':', ($calls === 2), ';';",
              "} finally { echo 'F;'; }", '$leftAlias = 6; $rightAlias = 4; $left = 8; $right = 9;',
              "echo 'END:', ($leftAlias === 6), ':', ($rightAlias === 4), ':', ($replacementLeft === 8), ':', ($replacementRight === 9), ':', ($v === 100), ';';"]
    assert lines[19].startswith('$second =') and lines[22].startswith('    $v =') and lines[23].strip() == '^=' and lines[24].strip() == '$right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'xorassign-selected-rhs-warning-canceled-precision': original()}
