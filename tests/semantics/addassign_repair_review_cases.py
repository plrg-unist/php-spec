"""Shared selected referents capture different numbers across two Warnings."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $c = $GLOBALS['calls'];
    echo 'H:', $c, ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ';';
    if ($c === 1) { $GLOBALS['alias'] = '5.5tail'; $GLOBALS['right'] =& $GLOBALS['replacementRight']; return true; }
    $GLOBALS['alias'] = 88; $GLOBALS['left'] =& $GLOBALS['replacementLeft']; return false;
}
$tail = 'tail'; $left = '12.5' . $tail;
$right =& $left; $alias =& $left;
$replacementLeft = 77; $replacementRight = 7; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = ($left', '        +=', '        $right);',
              "    echo 'R:', $v, ':', $v === 18.0, ':', $alias === 18.0, ':', $left === 77, ':', $right === 7, ':', $calls === 2, ';';",
              "} catch (Throwable $e) { echo 'BAD-E:', $e->getLine(), ';';",
              "} finally { echo 'F;'; }", '$alias = 6; $left = 8; $right = 9;',
              "echo 'END:', $alias === 6, ':', $replacementLeft === 8, ':', $replacementRight === 9, ':', $v === 18.0, ':', $calls === 2, ';';"]
    assert lines[22] == '    $v = ($left' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'addassign-repair-shared-cell': original()}
