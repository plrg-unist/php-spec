"""OP94 originals: a NaN CV printed through a named Warning callback."""


def normal():
    lines = '''<?php
function print_nan_handler($level, $message, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $level, ':', $line, ':', $message, ':', $file === __FILE__, ';';
    $GLOBALS['x'] = 0.0;
    unset($GLOBALS['x']);
    return false;
}
$x = NAN; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('print_nan_handler', E_WARNING);", 'try {',
              '    $v = (print', '        $x);',
              "    echo 'R:', $v === 1, ':', !isset($x), ':', $calls === 1, ';';",
              "} catch (Throwable $e) { echo 'BAD-E;'; }",
              "finally { echo 'F;'; }", '$x = 8;',
              "echo 'END:', $v === 1, ':', $x === 8, ':', $calls === 1, ';';"]
    assert lines[22] == '    $v = (print' and lines[23] == '        $x);'
    return ('\n'.join(lines) + '\n').encode()


def throwing():
    lines = '''<?php
function print_nan_handler($level, $message, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $level, ':', $line, ':', $message, ':', $file === __FILE__, ';';
    $GLOBALS['x'] = 0.0;
    unset($GLOBALS['x']);
    throw $GLOBALS['second'];
}
$x = NAN; $calls = 0; $v = 100;'''.splitlines()
    lines += [''] * (19 - len(lines))
    lines += ["$second = new Exception('print-nan');", "set_error_handler('print_nan_handler', E_WARNING);", 'try {',
              '    $v = (print', '        $x);',
              "    echo 'BAD-R;';", "} catch (Throwable $e) {",
              "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', !isset($x), ':', $calls === 1, ';';",
              "} finally { echo 'F;'; }", '$x = 8;',
              "echo 'END:', $x === 8, ':', $v === 100, ':', $calls === 1, ';';"]
    assert lines[22] == '    $v = (print' and lines[23] == '        $x);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'print-nan-false-default': normal(),
    'print-nan-pending-throw': throwing(),
}
