"""CONCAT reads a new Stringable RHS after the borrowed LEFT array warns."""


def original():
    lines = '''<?php
class O {
    public function __toString(): string {
        echo 'S:', $GLOBALS['right'] === $this, ';';
        $GLOBALS['casts'] = $GLOBALS['casts'] + 1; $GLOBALS['right'] = 'method'; $GLOBALS['left'] = 9;
        return 'B';
    }
}
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $n, ':', $m === 'Array to string conversion', ':', $line, ';';
    unset($GLOBALS['left']);
    $GLOBALS['right'] = new O;
    return false;
}

$left = []; $left[] = 7; $right = 'before'; $calls = 0; $casts = 0; $v = 100;'''.splitlines()
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = (', '        $left .', '        $right);',
              "    echo 'R:', $v === 'ArrayB', ':', $left === 9, ':', $right === 'method', ':', $calls === 1, ':', $casts === 1, ';';",
              "} catch (Throwable $e) { echo 'BAD-E;'; }", "finally { echo 'F;'; }", "$left = 8; $right = 'end';",
              "echo 'END:', $v === 'ArrayB', ':', $left === 8, ':', $right === 'end', ':', $calls === 1, ':', $casts === 1, ';';"]
    assert len(lines) == 30 and lines[23] == '        $left .' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {'concat-array-left-stringable-value': original()}
