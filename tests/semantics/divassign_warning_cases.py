"""Selected-reference /= commits only after both saved conversions succeed."""


def original(thrown):
    finish = "throw $GLOBALS['second'];" if thrown else 'return true;'
    lines = f'''<?php
function h($n, $m, $file, $line) {{
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $first = $GLOBALS['calls'] === 1;
    $ok = $first ? ($GLOBALS['leftAlias'] === '12.5tail' && $GLOBALS['rightAlias'] === 2) : ($GLOBALS['leftAlias'] === 99 && $GLOBALS['rightAlias'] === '5tail' && $GLOBALS['right'] === 7);
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ':', $ok, ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered' || $GLOBALS['calls'] > 2 || !$ok) {{ echo 'BAD-H;'; return true; }}
    if ($first) {{ $GLOBALS['leftAlias'] = 99; $GLOBALS['rightAlias'] = '5tail'; $GLOBALS['right'] =& $GLOBALS['replacementRight']; return true; }}
    $GLOBALS['leftAlias'] = 88; $GLOBALS['rightAlias'] = 7; $GLOBALS['left'] =& $GLOBALS['replacementLeft'];
    {finish}
}}
$tail = 'tail'; $left = '12.5' . $tail; $right = 2;
$leftAlias =& $left; $rightAlias =& $right;
$replacementLeft = 77; $replacementRight = 7; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (19 - len(lines))
    lines += ["$second = new Exception('divassign');" if thrown else '',
              "set_error_handler('h', 2);", 'try {', '    $v = ($left', '        /=', '        $right);']
    if thrown:
        lines += ["    echo 'BAD-R;';", '} catch (Throwable $e) {',
                  "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', $calls === 2, ':', $leftAlias === 88, ':', $left === 77, ':', $rightAlias === 7, ':', $right === 7, ';';",
                  "    $leftAlias = 73; echo 'T:', $leftAlias === 73, ':', $left === 77, ':', $v === 100, ';';"]
    else:
        lines += ["    echo 'R:', $v, ':', $v === 2.5, ':', $leftAlias === 2.5, ':', $left === 77, ':', $replacementLeft === 77, ':', $rightAlias === 7, ':', $right === 7, ':', $replacementRight === 7, ':', $calls === 2, ';';",
                  "} catch (Throwable $e) { echo 'BAD-E;';"]
    lines += ["} finally { echo 'F;'; }", '$leftAlias = 6; $rightAlias = 4;',
              "echo 'A:', $leftAlias === 6, ':', $rightAlias === 4, ':', $left === 77, ':', $right === 7, ';';",
              '$left = 8; $right = 9;',
              "echo 'B:', $left === 8, ':', $replacementLeft === 8, ':', $leftAlias === 6, ':', $right === 9, ':', $replacementRight === 9, ':', $rightAlias === 4, ':', " + ('$v === 100' if thrown else '$v === 2.5') + ", ';END;';"]
    assert lines[22] == '    $v = ($left' and lines[24] == '        $right);'
    assert not thrown or lines[19] == "$second = new Exception('divassign');"
    return ('\n'.join(lines) + '\n').encode()


CASES = {'divassign-warning-selected-float': original(False),
         'divassign-warning-second-throw': original(True)}
