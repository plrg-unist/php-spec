"""Two acquired CONCAT operands stay live until ordered VM retirement."""


def original():
    lines = '''<?php
class A {
    public function __toString(): string {
        $GLOBALS['leftcalls'] = $GLOBALS['leftcalls'] + 1;
        echo 'S;';
        return 'L';
    }
    public function __destruct() {
        $GLOBALS['adrops'] = $GLOBALS['adrops'] + 1;
        echo 'A:', $GLOBALS['v'] === 100, ':', $GLOBALS['bdrops'] === 0, ':', $GLOBALS['leftcalls'] === 1, ':', $GLOBALS['rightcalls'], ';';
    }
}
class B { public function __toString(): string { $GLOBALS['rightcalls'] = $GLOBALS['rightcalls'] + 1; echo 'T;'; return $GLOBALS['adrops'] === 0 ? 'R' : 'stale'; } public function __destruct() { $GLOBALS['bdrops'] = $GLOBALS['bdrops'] + 1; echo 'B:', $GLOBALS['v'] === 100, ':', $GLOBALS['adrops'] === 1, ':', $GLOBALS['leftcalls'] === 1, ':', $GLOBALS['rightcalls'], ';'; } }
function f() { echo 'P;'; return new A; }
function g() { echo 'Q;'; return new B; }'''.splitlines()
    lines += [''] * (17 - len(lines))
    lines += ["$leftcalls = 0; $rightcalls = 0; $adrops = 0; $bdrops = 0; $v = 100;", '', "$supplied = new Exception('kept');", '', 'try {', '    $v = (', '        f() .', '        g());',
              "    echo 'R:', $v === 'LR', ':', $leftcalls === 1, ':', $rightcalls === 1, ':', $adrops === 1, ':', $bdrops === 1, ';';",
              "} catch (Throwable $e) { echo 'BAD-E;'; }", "finally { echo 'F;'; }", '$leftcalls = 8; $rightcalls = 9;',
              "echo 'END:', $v === 'LR', ':', $leftcalls === 8, ':', $rightcalls === 9, ':', $adrops === 1, ':', $bdrops === 1, ';';"]
    assert len(lines) == 30
    assert lines[19] == "$supplied = new Exception('kept');"
    assert lines[23] == '        f() .' and lines[24] == '        g());'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'concat-two-acquired-stringables-ordered-retirement': original()}
