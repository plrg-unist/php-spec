"""Unary plus cancels delivery of a by-value return after source removal."""


def original():
    lines = '''<?php
function copied_value() { echo 'P;'; return $GLOBALS['source']; }
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $n, ':', $line, ':', $m, ';';
    $GLOBALS['source'] = 99; unset($GLOBALS['source']);
    throw $GLOBALS['second'];
}
$tail = 'tail'; $source = '12.5' . $tail;
$calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (19 - len(lines))
    lines += ["$second = new Exception('unary-copy');", "set_error_handler('h', 2);", 'try {', '    $v = (', '        +', '        copied_value());',
              "    echo 'BAD-R;';", '} catch (Throwable $e) {',
              "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', isset($source) === false, ':', $calls === 1, ';';",
              "} finally { echo 'F;'; }", '$source = 8;',
              "echo 'END:', $source === 8, ':', $v === 100, ':', $calls === 1, ';';"]
    assert lines[19] == "$second = new Exception('unary-copy');"
    assert lines[23] == '        +' and lines[24] == '        copied_value());'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'unary-copy-warning-return-throw': original()}
