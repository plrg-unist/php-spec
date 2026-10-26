"""Borrowed print retirement and acquired print cancellation stay distinct."""


def original(stringable_throws):
    lines = '''<?php
class A {
    public function __toString(): string {
        $GLOBALS['casts'] = $GLOBALS['casts'] + 1;
        echo 'S;';
        unset($GLOBALS['left']);'''.splitlines()
    lines += ["        throw $GLOBALS['supplied'];" if stringable_throws else "        return 'X;';"]
    lines += ['    }', '    public function __destruct() {',
              "        $GLOBALS['drops'] = $GLOBALS['drops'] + 1;",
              "        echo 'D:', $GLOBALS['v'] === 100, ':', $GLOBALS['casts'], ';';",
              '    }', '}', '', '', '',
              "function f() { echo 'P;'; return new A; }",
              '$casts = 0; $drops = 0; $v = 100;',
              '' if stringable_throws else '$left = new A;']
    label = 'print-S' if stringable_throws else 'print-borrowed'
    lines += ["$supplied = new Exception('" + label + "');", '', 'try {',
              '    $v = (', '        print',
              '        f());' if stringable_throws else '        $left);',
              "    echo 'BAD-R;';" if stringable_throws else "    echo 'R:', $v === 1, ':', !isset($left), ':', $casts === 1, ':', $drops === 1, ';';"]
    lines += ["} catch (Throwable $e) { echo 'C:', $e === $supplied, ':', $e->getPrevious() === null, ':', $e->getLine(), ':', $v === 100, ':', !isset($left), ':', $casts === 1, ':', $drops === 1, ';'; }" if stringable_throws else "} catch (Throwable $e) { echo 'BAD-E;'; }",
              "finally { echo 'F;'; }", '$left = 8;']
    value = '100' if stringable_throws else '1'
    lines += ["echo 'END:', $v === " + value + ", ':', $left === 8, ':', $casts === 1, ':', $drops === 1, ';';"]
    assert len(lines) == 30
    assert lines[19] == "$supplied = new Exception('" + label + "');"
    assert lines[23] == '        print'
    assert lines[24] == ('        f());' if stringable_throws else '        $left);')
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'print-borrowed-stringable-unset-control': original(False),
    'print-acquired-stringable-supplied-throw': original(True),
}
