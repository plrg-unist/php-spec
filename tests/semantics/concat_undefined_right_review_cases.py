"""CONCAT's fixed undefined RIGHT survives handler/method abrupt completion."""


def original(stringable_throws):
    lines = '''<?php
class A {
    public function __toString(): string {
        $GLOBALS['casts'] = $GLOBALS['casts'] + 1;
        echo 'S;';
        $GLOBALS['right'] = 'method';'''.splitlines()
    lines += ["        throw $GLOBALS['supplied'];" if stringable_throws else "        return 'L';"]
    lines += ['    }', '    public function __destruct() {',
              "        $GLOBALS['drops'] = $GLOBALS['drops'] + 1;",
              "        echo 'D:', $GLOBALS['v'] === 100, ':', $GLOBALS['casts'], ';';",
              '    }', '}', '', '']
    finish = 'return false;' if stringable_throws else "throw $GLOBALS['supplied'];"
    lines += ["function h($no, $s, $file, $line) { $GLOBALS['calls'] = $GLOBALS['calls'] + 1; echo 'H:', $no, ':', $line, ':', $s, ';'; $GLOBALS['right'] = 'handler'; " + finish + ' }',
              "function f() { echo 'P;'; return new A; }",
              '$calls = 0; $casts = 0; $drops = 0; $v = 100;',
              "set_error_handler('h');"]
    label = 'undefined-right-S' if stringable_throws else 'undefined-right-H'
    lines += ["$supplied = new Exception('" + label + "');", '', 'try {',
              '    $v = (', '        f() .', '        $right);', "    echo 'BAD-R;';"]
    count = '1' if stringable_throws else '0'
    value = 'method' if stringable_throws else 'handler'
    lines += ["} catch (Throwable $e) { echo 'C:', $e === $supplied, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', $right === '" + value + "', ':', $calls === 1, ':', $casts === " + count + ", ':', $drops === 1, ';'; }",
              "finally { echo 'F;'; }", '$right = 8;',
              "echo 'END:', $v === 100, ':', $right === 8, ':', $calls === 1, ':', $casts === " + count + ", ':', $drops === 1, ';';"]
    assert len(lines) == 30
    assert lines[19] == "$supplied = new Exception('" + label + "');"
    assert lines[23] == '        f() .' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'concat-undefined-right-handler-throw': original(False),
    'concat-undefined-right-stringable-throw': original(True),
}
