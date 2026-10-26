"""Undefined RIGHT is selected before LEFT string conversion can run."""


def original():
    lines = '''<?php
class A {
    public function __toString(): string {
        $GLOBALS['casts'] = $GLOBALS['casts'] + 1;
        echo 'S;';
        $GLOBALS['right'] = 'method';
        return 'L';
    }
    public function __destruct() {
        $GLOBALS['drops'] = $GLOBALS['drops'] + 1;
        echo 'D:', $GLOBALS['v'] === 100, ':', $GLOBALS['casts'], ';';
    }
}


function h($no, $s, $file, $line) { $GLOBALS['calls'] = $GLOBALS['calls'] + 1; echo 'H:', $no, ':', $line, ':', $s, ';'; $GLOBALS['right'] = 'handler'; return false; }
function f() { echo 'P;'; return new A; }
$calls = 0; $casts = 0; $drops = 0; $v = 100;
set_error_handler('h');
$supplied = new Exception('kept');

try {
    $v = (
        f() .
        $right);
    echo 'R:', $v === 'L', ':', $right === 'method', ':', $calls === 1, ':', $casts === 1, ':', $drops === 1, ';';
} catch (Throwable $e) { echo 'BAD-E;'; }
finally { echo 'F;'; }
$right = 8;
echo 'END:', $v === 'L', ':', $right === 8, ':', $calls === 1, ':', $casts === 1, ':', $drops === 1, ';';'''.splitlines()
    assert len(lines) == 30
    assert lines[19] == "$supplied = new Exception('kept');"
    assert lines[23] == '        f() .' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'concat-undefined-right-before-left': original()}
