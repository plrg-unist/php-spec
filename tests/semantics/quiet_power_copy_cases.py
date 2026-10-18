"""Quiet ternary copies enter final power deprecation without a Warning."""


def original(throw):
    lines = f'''<?php
function h($n, $m, $file, $line) {{
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":", ($m === 'Power of base 0 and negative exponent is deprecated'), ":", ($GLOBALS['left'] === '0.0' && $GLOBALS['right'] === -2), ";";
    $GLOBALS['left'] = 77; $GLOBALS['right'] = 9;
    if ($GLOBALS['throwAt']) {{ throw $GLOBALS['supplied']; }}
    return true;
}}
$tail = '.0'; $left = '0' . $tail; $right = -2;
$pick = true; $calls = 0; $throwAt = {str(throw).lower()}; $v = 100;'''.splitlines()
    lines += [''] * (19 - len(lines))
    lines += ['$supplied = new Exception("supplied");', 'set_error_handler("h", E_DEPRECATED);', 'try {',
              '    $v = (($pick ? $left : 7)', '        **', '        $right);',
              '    echo "R:", $v, ":", ($v === 1e999), ":", ($calls === 1), ":", ($left === 77), ":", ($right === 9), ";";',
              '} catch (Throwable $e) {',
              '    echo "C:", ($e === $supplied), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", ($calls === 1), ":", ($left === 77), ":", ($right === 9), ";";',
              '} finally { echo "F;"; }', '$left = 1; $right = 2;',
              'echo "A:", ($left === 1), ":", ($right === 2), ";END;";']
    assert lines[19].startswith('$supplied =') and lines[22].startswith('    $v =')
    assert lines[24].strip() == '$right);'
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'quiet-power-copy-positive': original(False),
    'quiet-power-copy-throw': original(True),
}
