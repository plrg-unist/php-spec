"""Acquired LEFT versus borrowed CV lifetime across the live RIGHT read."""


def original(acquired):
    wanted = 'Lfresh' if acquired else 'Lretired'
    left = 'f()' if acquired else '$left'
    initial = '' if acquired else ' $left = new A;'
    lines = '''<?php
class A {
    public function __toString(): string {
        $GLOBALS['leftcalls'] = $GLOBALS['leftcalls'] + 1;
        echo 'S;';
        $GLOBALS['right'] = 'fresh';
        unset($GLOBALS['left']);
        return 'L';
    }
    public function __destruct() {
        $GLOBALS['drops'] = $GLOBALS['drops'] + 1;
        echo 'D:', $GLOBALS['v'] === 100, ':', $GLOBALS['rightcalls'], ';';
        $GLOBALS['right'] = 'retired';
    }
}

function f() { echo 'P;'; return new A; }
$leftcalls = 0; $rightcalls = 0; $drops = 0; $right = 'old'; $v = 100;'''.splitlines()
    lines[-1] += initial
    lines += [''] * (21 - len(lines))
    lines += ['try {', '    $v = (', '        ' + left + ' .', '        $right);',
              "    echo 'R:', $v === '" + wanted + "', ':', isset($left) === false, ':', $right === 'retired', ':', $leftcalls === 1, ':', $rightcalls === 0, ':', $drops === 1, ';';",
              "} catch (Throwable $e) { echo 'BAD-E;'; }", "finally { echo 'F;'; }", "$left = 8; $right = 9;",
              "echo 'END:', $v === '" + wanted + "', ':', $left === 8, ':', $right === 9, ':', $leftcalls === 1, ':', $rightcalls === 0, ':', $drops === 1, ';';"]
    assert len(lines) == 30 and lines[23] == '        ' + left + ' .' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'concat-acquired-left-live-right': original(True),
    'concat-borrowed-left-live-right-control': original(False),
}
