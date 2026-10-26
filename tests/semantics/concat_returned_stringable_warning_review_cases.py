"""Acquired Stringable TMP retirement on CONCAT method and handler throws."""


def original(stringable_throws):
    lines = '''<?php
class O {
    public function __toString(): string {
        echo 'S:', $GLOBALS['seed'] === 'changed', ';'; $GLOBALS['casts'] = $GLOBALS['casts'] + 1;'''.splitlines()
    lines += ["        throw $GLOBALS['second'];" if stringable_throws else "        return 'B';"]
    lines += ['    }', '    public function __destruct() {',
              "        $GLOBALS['drops'] = $GLOBALS['drops'] + 1; echo 'D:', $GLOBALS['v'] === 100, ':', $GLOBALS['casts'], ';';",
              '    }', '}', "function f() { echo 'P;'; return $GLOBALS['seed']; }",
              'function h($n, $m, $file, $line) {',
              "    $GLOBALS['calls'] = $GLOBALS['calls'] + 1; echo 'H:', $n, ':', $m === 'Array to string conversion', ':', $line, ';';",
              "    unset($GLOBALS['left']); $GLOBALS['seed'] = 'changed';",
              '    return false;' if stringable_throws else "    throw $GLOBALS['second'];", '}',
              "$left = []; $left[] = 7; $seed = new O; $calls = 0; $casts = 0; $drops = 0; $v = 100;"]
    lines += [''] * (19 - len(lines))
    label = 'concat-TMP-S' if stringable_throws else 'concat-TMP-H'
    lines += ["$second = new Exception('" + label + "');", "set_error_handler('h', 2);", 'try {',
              '    $v = (', '        $left .', '        f());', "    echo 'BAD-R;';", '} catch (Throwable $e) {']
    count = '1' if stringable_throws else '0'
    lines += ["    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', isset($left) === false, ':', $seed === 'changed', ':', $calls === 1, ':', $casts === " + count + ", ':', $drops === 1, ';';",
              "} finally { echo 'F;'; }", "$left = 8; $seed = 'end';",
              "echo 'END:', $v === 100, ':', $left === 8, ':', $seed === 'end', ':', $calls === 1, ':', $casts === " + count + ", ':', $drops === 1, ';';"]
    assert lines[19] == "$second = new Exception('" + label + "');"
    assert lines[23] == '        $left .' and lines[24] == '        f());'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'concat-array-left-returned-stringable-throw': original(True),
    'concat-array-left-handler-throw-before-returned-stringable': original(False),
}
