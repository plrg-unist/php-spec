"""A delayed failed += conversion must not retry live array union."""


def original():
    lines = '''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ':', ($GLOBALS['left'] === '12.5tail' && $GLOBALS['right'] === 2), ';';
    if ($n !== 2 || $line !== 25 || $GLOBALS['calls'] !== 1 || $m !== 'A non-numeric value encountered') { echo 'BAD-H;'; return true; }
    $GLOBALS['left'] = [1]; $GLOBALS['right'] = [2];
    return true;
}
$tail = 'tail'; $left = '12.5' . $tail; $right = 2;
$calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = ($left', '        +=', '        $right);',
              "    echo 'BAD-R;';", '} catch (Throwable $e) {',
              "    echo 'E:', $e instanceof TypeError, ':', $e->getMessage() === 'Unsupported operand types: array + array', ':', $e->getLine(), ':', $e->getPrevious() === null, ':', $v === 100, ':', $calls === 1, ':', $left[0] === 1, ':', $right[0] === 2, ';';",
              "} finally { echo 'F;'; }",
              "echo 'A:', $left[0] === 1, ':', $right[0] === 2, ':', $v === 100, ';END;';"]
    assert lines[22] == '    $v = ($left' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'addassign-rhs-failure-array-pair': original()}
