"""OP96 originals: first echo array warning controls a later echo expression."""


def source(throwing):
    action = "throw $GLOBALS['second'];" if throwing else "return false;"
    lines = f'''<?php
function echo_array_handler($level, $message, $file, $line) {{
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $level, ':', $line, ':', $message, ':', $file === __FILE__, ';';
    $GLOBALS['b'] = 'after';
    $GLOBALS['a'] = 99;
    unset($GLOBALS['a']);
    {action}
}}
function later() {{
    $GLOBALS['later_calls'] = $GLOBALS['later_calls'] + 1;
    echo 'L;';
    return $GLOBALS['b'];
}}
$a = [11, 22]; $b = 'before'; $calls = 0; $later_calls = 0;'''.splitlines()
    lines += [''] * ((19 if throwing else 20) - len(lines))
    if throwing:
        lines += ["$second = new Exception('echo-array');"]
    lines += ["set_error_handler('echo_array_handler', E_WARNING);", 'try {',
              '    echo', '        $a,', "        '|',", '        later();']
    if throwing:
        lines += ["    echo 'BAD-R;';", "} catch (Throwable $e) {",
                  "    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $later_calls === 0, ':', !isset($a), ':', $b === 'after', ':', $calls === 1, ';';",
                  '}']
    else:
        lines += ["    echo 'R:', $later_calls === 1, ':', !isset($a), ':', $b === 'after', ':', $calls === 1, ';';",
                  "} catch (Throwable $e) { echo 'BAD-E;'; }"]
    lines += ["finally { echo 'F;'; }", "$a = 8;",
              "echo 'END:', $a === 8, ':', $later_calls === " + ('0' if throwing else '1') + ", ':', $calls === 1, ';';"]
    assert lines[23] == '        $a,'
    if throwing:
        assert lines[19] == "$second = new Exception('echo-array');"
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'echo-array-first-false-default': source(False),
    'echo-array-first-pending-throw': source(True),
}
