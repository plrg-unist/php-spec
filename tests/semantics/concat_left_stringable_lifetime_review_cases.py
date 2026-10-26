"""Acquired LEFT retirement after RIGHT throw or an earlier LEFT throw."""


def original(left_throws):
    lines = '''<?php
class A {
    public function __toString(): string {
        $GLOBALS['leftcalls'] = $GLOBALS['leftcalls'] + 1;
        echo 'S;';
        $GLOBALS['right'] = new B;
        unset($GLOBALS['left']);'''.splitlines()
    lines += ["        throw $GLOBALS['second'];" if left_throws else "        return 'L';"]
    lines += ['    }', '    public function __destruct() {',
              "        $GLOBALS['drops'] = $GLOBALS['drops'] + 1;",
              "        echo 'D:', $GLOBALS['v'] === 100, ':', $GLOBALS['rightcalls'], ';';",
              "        $GLOBALS['right'] = 'retired';", '    }', '}',
              "class B { public function __toString(): string { $GLOBALS['rightcalls'] = $GLOBALS['rightcalls'] + 1; echo 'T;'; throw $GLOBALS['second']; } }",
              "function f() { echo 'P;'; return new A; }",
              "$leftcalls = 0; $rightcalls = 0; $drops = 0; $right = 'old'; $v = 100;"]
    lines += [''] * (19 - len(lines))
    label = 'concat-left' if left_throws else 'concat-right'
    lines += ["$second = new Exception('" + label + "');", '', 'try {',
              '    $v = (', '        f() .', '        $right);', "    echo 'BAD-R;';", '} catch (Throwable $e) {']
    count = '0' if left_throws else '1'
    lines += ["    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', isset($left) === false, ':', $right === 'retired', ':', $leftcalls === 1, ':', $rightcalls === " + count + ", ':', $drops === 1, ';';",
              "} finally { echo 'F;'; }", "$left = 8; $right = 9;",
              "echo 'END:', $v === 100, ':', $left === 8, ':', $right === 9, ':', $leftcalls === 1, ':', $rightcalls === " + count + ", ':', $drops === 1, ';';"]
    assert lines[19] == "$second = new Exception('" + label + "');"
    assert lines[23] == '        f() .' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'concat-acquired-left-right-throw': original(False),
    'concat-acquired-left-left-throw': original(True),
}
