"""NaN bitwise-NOT pending exception with ineligible versus eligible next notice."""


def original(mask):
    lines = """<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m, ';';
    $GLOBALS['x'] = 99;
    throw $GLOBALS['second'];
}
$x = NAN; $v = 100; $calls = 0;""".splitlines()
    lines += [''] * (19 - len(lines))
    lines += ["$second = new Exception('chosen');", "set_error_handler('h', " + str(mask) + ");", 'try {',
              '    $v = (', '        ~', '        $x);', "    echo 'BAD-R;';",
              "} catch (Throwable $e) { echo 'C:', ($e === $second), ':', ($e->getPrevious() === null), ':', $e->getLine(), ':', ($v === 100), ':', ($x === 99), ':', ($calls === 1), ';';",
              "} finally { echo 'F;'; }", "echo 'END:', ($x === 99), ':', ($v === 100), ':', ($calls === 1), ';';"]
    assert lines[19].startswith('$second =') and lines[23].strip() == '~' and lines[24].strip() == '$x);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'bitnot-nan-pending-ineligible-precision': original(2),
    'bitnot-nan-pending-eligible-precision': original(8194),
}
