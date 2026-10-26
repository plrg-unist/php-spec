"""OP95 originals: a plain CV array printed through a named Warning callback."""


def normal():
    lines = '''<?php
function print_array_handler($level, $message, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $level, ':', $line, ':', $message, ':', $file === __FILE__, ';';
    $GLOBALS['a'] = 99;
    unset($GLOBALS['a']);
    return false;
}
$a = [11, 22]; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('print_array_handler', E_WARNING);", 'try {',
              '    $v = (print', '        $a);',
              "    echo 'R:', $v === 1, ':', !isset($a), ':', $calls === 1, ';';",
              "} catch (Throwable $e) { echo 'BAD-E;'; }",
              "finally { echo 'F;'; }", '$a = 8;',
              "echo 'END:', $v === 1, ':', $a === 8, ':', $calls === 1, ';';"]
    assert lines[22] == '    $v = (print' and lines[23] == '        $a);'
    return ('\n'.join(lines) + '\n').encode()


def throwing():
    lines = '''<?php
function print_array_handler($level, $message, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $level, ':', $line, ':', $message, ':', $file === __FILE__, ';';
    $GLOBALS['a'] = 99;
    unset($GLOBALS['a']);
    throw $GLOBALS['second'];
}
$a = [11, 22]; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (19 - len(lines))
    lines += ["$second = new Exception('print-array');", "set_error_handler('print_array_handler', E_WARNING);", 'try {',
              '    $v = (print', '        $a);',
              "    echo 'BAD-R;';", "} catch (Throwable $e) {",
              "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', !isset($a), ':', $calls === 1, ';';",
              "} finally { echo 'F;'; }", '$a = 8;',
              "echo 'END:', $a === 8, ':', $v === 100, ':', $calls === 1, ';';"]
    assert lines[22] == '    $v = (print' and lines[23] == '        $a);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'print-array-false-default': normal(),
    'print-array-pending-throw': throwing(),
}
