"""Initial invalid RHS text is read only after the selected LEFT Warning."""


def original(throw):
    lines = f'''<?php
function h($n, $m, $file, $line) {{
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":", ($m === 'A non-numeric value encountered'), ":", (($GLOBALS['calls'] === 1 && $GLOBALS['left'] === '12tail' && $GLOBALS['right'] === 'bad5') || ($GLOBALS['calls'] === 2 && $GLOBALS['left'] === 99 && $GLOBALS['right'] === '5tail')), ";";
    if ($GLOBALS['calls'] === 1) {{
        $GLOBALS['left'] = 99; $GLOBALS['right'] = '5tail';
        if ($GLOBALS['throwAt']) {{ throw $GLOBALS['supplied']; }}
    }} else {{ $GLOBALS['left'] = 88; $GLOBALS['right'] = 7; }}
    return true;
}}
$tail = 'tail'; $tag = '5'; $left = '12' . $tail; $right = 'bad' . $tag;
$leftAlias =& $left; $rightAlias =& $right;
$calls = 0; $throwAt = {str(throw).lower()}; $v = 100;'''.splitlines()
    lines += [''] * (19 - len(lines))
    lines += ['$supplied = new Exception("supplied");', 'set_error_handler("h", E_WARNING);', 'try {',
              '    $v = ($left', '        /', '        $right);',
              '    echo "R:", $v, ":", ($v === 2.4), ":", ($calls === 2), ":", ($left === 88), ":", ($right === 7), ":", ($leftAlias === 88), ":", ($rightAlias === 7), ";";',
              '} catch (Throwable $e) {',
              '    echo "C:", ($e === $supplied), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", ($calls === 1), ":", ($left === 99), ":", ($right === \'5tail\'), ":", ($leftAlias === 99), ":", ($rightAlias === \'5tail\'), ";";',
              '} finally { echo "F;"; }', '$left = 1; $right = 2;',
              'echo "A:", ($leftAlias === 1), ":", ($rightAlias === 2), ";END;";']
    assert lines[19].startswith('$supplied =') and lines[22].startswith('    $v =')
    assert lines[24].strip() == '$right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'div-repair-cached-float': original(False),
    'div-repair-first-throw': original(True),
}
