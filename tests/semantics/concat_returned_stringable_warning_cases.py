"""A returned CONCAT operand outlives its source and retires before store."""


def original():
    lines = '''<?php
class O {
    public function __toString(): string {
        echo 'S:', $GLOBALS['seed'] === 'changed', ';'; $GLOBALS['casts'] = $GLOBALS['casts'] + 1;
        return 'B';
    }
    public function __destruct() {
        $GLOBALS['drops'] = $GLOBALS['drops'] + 1; echo 'D:', $GLOBALS['v'] === 100, ':', $GLOBALS['casts'], ';';
    }
}
function f() { echo 'P;'; return $GLOBALS['seed']; }
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1; echo 'H:', $n, ':', $m === 'Array to string conversion', ':', $line, ';';
    unset($GLOBALS['left']); $GLOBALS['seed'] = 'changed';
    return false;
}
$left = []; $left[] = 7; $seed = new O; $calls = 0; $casts = 0; $drops = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = (', '        $left .', '        f());',
              "    echo 'R:', $v === 'ArrayB', ':', isset($left) === false, ':', $seed === 'changed', ':', $calls === 1, ':', $casts === 1, ':', $drops === 1, ';';",
              "} catch (Throwable $e) { echo 'BAD-E;'; }", "finally { echo 'F;'; }", "$left = 8; $seed = 'end';",
              "echo 'END:', $v === 'ArrayB', ':', $left === 8, ':', $seed === 'end', ':', $calls === 1, ':', $casts === 1, ':', $drops === 1, ';';"]
    assert len(lines) == 30 and lines[23] == '        $left .' and lines[24] == '        f());'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'concat-array-returned-stringable-value': original()}
