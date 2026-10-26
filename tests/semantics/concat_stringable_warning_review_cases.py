"""Stringable and earlier Warning throws cancel distinct CONCAT stages."""


def original(stringable_throws):
    lines = '''<?php
class O {
    public function __toString(): string {
        echo 'S:', $GLOBALS['right'] === $this, ';';
        $GLOBALS['casts'] = $GLOBALS['casts'] + 1; $GLOBALS['right'] = 'method'; $GLOBALS['left'] = 9;'''.splitlines()
    lines += ["        throw $GLOBALS['second'];" if stringable_throws else "        return 'B';"]
    lines += ['    }', '}', 'function h($n, $m, $file, $line) {',
              "    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;",
              "    echo 'H:', $n, ':', $m === 'Array to string conversion', ':', $line, ';';",
              "    unset($GLOBALS['left']);", "    $GLOBALS['right'] = new O;",
              '    return false;' if stringable_throws else "    throw $GLOBALS['second'];", '}', '',
              "$left = []; $left[] = 7; $right = 'before'; $calls = 0; $casts = 0; $v = 100;"]
    lines += [''] * (19 - len(lines))
    label = 'concat-S' if stringable_throws else 'concat-H'
    lines += ["$second = new Exception('" + label + "');", "set_error_handler('h', 2);", 'try {',
              '    $v = (', '        $left .', '        $right);', "    echo 'BAD-R;';", '} catch (Throwable $e) {']
    left_check = '$left === 9' if stringable_throws else 'isset($left) === false'
    right_check = "$right === 'method'" if stringable_throws else '$right instanceof O'
    count = '1' if stringable_throws else '0'
    lines += ["    echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', " + left_check + ", ':', " + right_check + ", ':', $calls === 1, ':', $casts === " + count + ", ';';",
              "} finally { echo 'F;'; }", "$left = 8; $right = 'end';",
              "echo 'END:', $left === 8, ':', $right === 'end', ':', $v === 100, ':', $calls === 1, ':', $casts === " + count + ", ';';"]
    assert lines[19] == "$second = new Exception('" + label + "');"
    assert lines[23] == '        $left .' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'concat-array-left-stringable-throw': original(True),
    'concat-array-left-handler-throw-before-stringable': original(False),
}
