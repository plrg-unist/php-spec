"""Second += Warning preserves cached numbers across late aliases or RHS unset."""


def original(alias):
    initial = "($GLOBALS['calls'] === 1 ? ($GLOBALS['left'] === '12.5tail' && $GLOBALS['right'] === 2) : ($GLOBALS['left'] === 99 && $GLOBALS['right'] === '5.5tail'))"
    lines = f'''<?php
function h($n, $m, $file, $line) {{
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'A non-numeric value encountered', ':', {initial}, ';';
    if ($n !== 2 || $line !== 25 || $m !== 'A non-numeric value encountered' || ($GLOBALS['calls'] !== 1 && $GLOBALS['calls'] !== 2)) {{ echo 'BAD-H;'; return true; }}
    if ($GLOBALS['calls'] === 1) {{ $GLOBALS['left'] = 99; $GLOBALS['right'] = '5.5tail'; return true; }}'''.splitlines()
    if alias:
        lines += ["    $GLOBALS['left'] = 88; $GLOBALS['alias'] =& $GLOBALS['left'];",
                  "    $GLOBALS['right'] =& $GLOBALS['left']; return false;"]
    else:
        lines += ["    $GLOBALS['left'] = 88; unset($GLOBALS['right']); return false;"]
    lines += ['}', "$tail = 'tail'; $left = '12.5' . $tail; $right = 2;", '$calls = 0; $v = 100;']
    lines += [''] * (20 - len(lines))
    lines += ["set_error_handler('h', 2);", 'try {', '    $v = ($left', '        +=', '        $right);']
    if alias:
        lines += ["    echo 'R:', $v, ':', $v === 18.0, ':', $left === 18.0, ':', $alias === 88, ':', $right === 88, ':', $calls === 2, ';';"]
    else:
        lines += ["    echo 'R:', $v, ':', $v === 18.0, ':', $left === 18.0, ':', isset($right) === false, ':', $calls === 2, ';';"]
    lines += ["} catch (Throwable $e) { echo 'BAD-E:', $e->getLine(), ';';", "} finally { echo 'F;'; }"]
    if alias:
        lines += ['$left = 1;', "echo 'A:', $left === 1, ':', $alias === 88, ':', $right === 88, ';';",
                  '$alias = 6;', "echo 'B:', $left === 1, ':', $alias === 6, ':', $right === 6, ';END;';"]
    else:
        lines += ['$left = 1;', "echo 'A:', $left === 1, ':', isset($right) === false, ';END;';"]
    assert lines[22] == '    $v = ($left' and lines[24] == '        $right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'addassign-rhs-warning-late-references': original(True),
    'addassign-rhs-warning-unset-right': original(False),
}
