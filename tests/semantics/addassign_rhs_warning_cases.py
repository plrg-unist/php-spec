"""Plain compound ADD captures a newly warning RHS before storage."""


def original(throw):
    lines = f'''<?php
function h($n, $m, $file, $line) {{
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":", ($m === 'A non-numeric value encountered'), ":", (($GLOBALS['calls'] === 1 && $GLOBALS['left'] === '12.5tail' && $GLOBALS['right'] === 2) || ($GLOBALS['calls'] === 2 && $GLOBALS['left'] === 99 && $GLOBALS['right'] === '5.5tail')), ";";
    if ($GLOBALS['calls'] === 1) {{
        $GLOBALS['left'] = 99; $GLOBALS['right'] = '5.5tail';
    }} else {{
        if ($GLOBALS['throwAt']) {{
            $GLOBALS['alias'] =& $GLOBALS['left'];
            $GLOBALS['left'] = 88; $GLOBALS['right'] = 7;
            throw $GLOBALS['supplied'];
        }}
        $GLOBALS['left'] = false; $GLOBALS['right'] = 7;
    }}
    return true;
}}
$tail = 'tail'; $left = '12.5' . $tail; $right = 2;
$calls = 0; $throwAt = {str(throw).lower()}; $alias = 0; $v = 100;'''.splitlines()
    lines += [''] * (19 - len(lines))
    lines += ['$supplied = new Exception("supplied");', 'set_error_handler("h", E_WARNING);', 'try {',
              '    $v = ($left', '        +=', '        $right);',
              '    echo "R:", $v, ":", ($v === 18.0), ":", ($left === 18.0), ":", ($right === 7), ":", ($alias === 0), ":", ($calls === 2), ";";',
              '} catch (Throwable $e) {',
              '    echo "C:", ($e === $supplied), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", ($calls === 2), ":", ($left === 88), ":", ($right === 7), ":", ($alias === 88), ";";',
              '    $left = 73; echo "B:", ($alias === 73), ";";',
              '} finally { echo "F;"; }', '$left = 7; $right = 8;',
              'echo "A:", ($throwAt ? $alias === 7 : $alias === 0), ":", ($right === 8), ";END;";']
    assert lines[19].startswith('$supplied =') and lines[22].startswith('    $v =')
    assert lines[24].strip() == '$right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'addassign-rhs-warning-cached-float': original(False),
    'addassign-rhs-warning-second-throw': original(True),
}
