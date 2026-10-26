"""Used print owns an acquired operand until after writing its text."""


def original():
    lines = '''<?php
class A {
    public function __toString(): string {
        $GLOBALS['casts'] = $GLOBALS['casts'] + 1;
        echo 'S;';
        unset($GLOBALS['left']);
        return 'X;';
    }
    public function __destruct() {
        $GLOBALS['drops'] = $GLOBALS['drops'] + 1;
        echo 'D:', $GLOBALS['v'] === 100, ':', $GLOBALS['casts'], ';';
    }
}



function f() { echo 'P;'; return new A; }
$casts = 0; $drops = 0; $v = 100;

$supplied = new Exception('kept');

try {
    $v = (
        print
        f());
    echo 'R:', $v === 1, ':', !isset($left), ':', $casts === 1, ':', $drops === 1, ';';
} catch (Throwable $e) { echo 'BAD-E;'; }
finally { echo 'F;'; }
$left = 8;
echo 'END:', $v === 1, ':', $left === 8, ':', $casts === 1, ':', $drops === 1, ';';'''.splitlines()
    assert len(lines) == 30
    assert lines[19] == "$supplied = new Exception('kept');"
    assert lines[23] == '        print' and lines[24] == '        f());'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'print-acquired-stringable-before-retirement': original()}
