"""Both acquired operands retire in operand order despite reversed allocation."""


def original(left_throws):
    lines = '''<?php
class A {
    public function __toString(): string {
        $GLOBALS['leftcalls'] = $GLOBALS['leftcalls'] + 1;
        echo 'S;';'''.splitlines()
    lines += ["        throw $GLOBALS['supplied'];" if left_throws else "        return 'L';"]
    lines += ['    }', '    public function __destruct() {',
              "        $GLOBALS['adrops'] = $GLOBALS['adrops'] + 1;",
              "        echo 'A:', $GLOBALS['v'] === 100, ':', $GLOBALS['bdrops'] === 0, ':', $GLOBALS['leftcalls'] === 1, ':', $GLOBALS['rightcalls'], ';';",
              '    }', '}']
    right_return = "return 'R';" if left_throws else "throw $GLOBALS['supplied'];"
    lines += ["class B { public function __toString(): string { $GLOBALS['rightcalls'] = $GLOBALS['rightcalls'] + 1; echo 'T;'; " + right_return + " } public function __destruct() { $GLOBALS['bdrops'] = $GLOBALS['bdrops'] + 1; echo 'B:', $GLOBALS['v'] === 100, ':', $GLOBALS['adrops'] === 1, ':', $GLOBALS['leftcalls'] === 1, ':', $GLOBALS['rightcalls'], ';'; } }",
              "function f() { echo 'P;'; return new A; }",
              "function g() { echo 'Q;'; $saved = $GLOBALS['seed']; unset($GLOBALS['seed']); return $saved; }"]
    lines += [''] * (17 - len(lines))
    label = 'dual-left' if left_throws else 'dual-right'
    lines += ["$leftcalls = 0; $rightcalls = 0; $adrops = 0; $bdrops = 0; $v = 100; $seed = new B;", '',
              "$supplied = new Exception('" + label + "');", '', 'try {',
              '    $v = (', '        f() .', '        g());', "    echo 'BAD-R;';", '} catch (Throwable $e) {']
    count = '0' if left_throws else '1'
    lines += ["    echo 'C:', $e === $supplied, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', $leftcalls === 1, ':', $rightcalls === " + count + ", ':', $adrops === 1, ':', $bdrops === 1, ':', isset($seed) === false, ';';",
              "} finally { echo 'F;'; }", '$leftcalls = 8; $rightcalls = 9; $seed = 10;',
              "echo 'END:', $v === 100, ':', $leftcalls === 8, ':', $rightcalls === 9, ':', $adrops === 1, ':', $bdrops === 1, ':', $seed === 10, ';';"]
    assert len(lines) == 31
    assert lines[19] == "$supplied = new Exception('" + label + "');"
    assert lines[23] == '        f() .' and lines[24] == '        g());'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'concat-two-acquired-right-throw': original(False),
    'concat-two-acquired-left-throw': original(True),
}
