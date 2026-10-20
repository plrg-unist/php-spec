"""Selected-reference power assignment distinguishes conversion and final-handler throws."""


def original(final_throw):
    second = "return true;" if final_throw else "throw $GLOBALS['second'];"
    expected = "1e999" if final_throw else "88"
    calls = 3 if final_throw else 2
    lines = """<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    $c = $GLOBALS['calls'];
    echo 'H:', $c, ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered' || $m === 'Power of base 0 and negative exponent is deprecated', ';';
    if ($c === 1) { $GLOBALS['leftAlias'] = 99; $GLOBALS['rightAlias'] = '-2tail'; $GLOBALS['right'] =& $GLOBALS['replacementRight']; return true; }
    if ($c === 2) { $GLOBALS['leftAlias'] = 88; $GLOBALS['rightAlias'] = 7; $GLOBALS['left'] =& $GLOBALS['replacementLeft']; SECOND }
    $GLOBALS['leftAlias'] = 66; throw $GLOBALS['second'];
}
$tail = 'tail'; $left = '0' . $tail; $right = 2;
$leftAlias =& $left; $rightAlias =& $right;
$replacementLeft = 77; $replacementRight = 7; $calls = 0; $v = 100;""".replace('SECOND', second).splitlines()
    lines += [''] * (19 - len(lines))
    lines += ["$second = new Exception('powerassign-conversion');", "set_error_handler('h', 8194);", 'try {', '    $v = ($left', '        **=', '        $right);',
              "    echo 'BAD-R;';", '} catch (Throwable $e) {',
              f"    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', $calls === {calls}, ':', $leftAlias === {expected}, ':', $left === 77, ':', $rightAlias === 7, ':', $right === 7, ';';",
              "} finally { echo 'F;'; }", '$leftAlias = 6; $rightAlias = 4; $left = 8; $right = 9;',
              "echo 'END:', $leftAlias === 6, ':', $rightAlias === 4, ':', $replacementLeft === 8, ':', $replacementRight === 9, ':', $v === 100, ';';"]
    assert lines[19] == "$second = new Exception('powerassign-conversion');"
    assert lines[22] == '    $v = ($left' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'powerassign-conversion-second-throw': original(False),
         'powerassign-conversion-final-throw': original(True)}
