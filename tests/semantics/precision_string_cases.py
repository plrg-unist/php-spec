"""Protected fractional text through one or two delayed RHS diagnostics."""


def original(operator, text, result, *, carrier=False, throw_at=0):
    producer = "'0' . $GLOBALS['tail']" if carrier else repr(text)
    final_right = 7 if operator == '%' else 1 if operator == '>>' else 10
    message = 'Implicit conversion from float-string "' + text + '" to int loses precision'
    lines = f'''<?php
function h($n, $m, $file, $line) {{
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo "H:", $GLOBALS['calls'], ":", $n, ":", $line, ":";
    if ($GLOBALS['calls'] === 1) {{
        echo ($m === "Implicit conversion from float 12.5 to int loses precision"), ";";
        $GLOBALS['alias'] =& $GLOBALS['left']; $GLOBALS['left'] = 99;
        $GLOBALS['right'] = {producer}; return true;
    }}
    if ($n === 2) {{
        echo ($m === "A non-numeric value encountered"), ";";
        $GLOBALS['left'] = 88; $GLOBALS['right'] = "7.5replaced";
        if ($GLOBALS['throw_at'] === 2) {{ throw $GLOBALS['second']; }} return true;
    }}
    echo (($n === 8192) && ($m === '{message}')), ";";
    $GLOBALS['left'] = 101; $GLOBALS['right'] = {final_right};
    if ($GLOBALS['throw_at'] === 3) {{ throw $GLOBALS['second']; }} return true;
}}
$calls = 0; $throw_at = {throw_at}; $tail = '5.5tail'; $left = 12.5; $right = 8.5; $v = 100;
$second = new Exception("supplied");
set_error_handler("h");'''.splitlines()
    # Keep all normal and abrupt originals at the same multiline RHS occurrence.
    assert len(lines) <= 21
    lines += [''] * (21 - len(lines))
    lines += [
        'try {',
        '    $v = ($left',
        '        ' + operator + '=',
        '        $right);',
        f'    echo "R:", $v, ":", ($v === {result}), ":", $left, ":", $alias, ":", $right, ":", $calls, ";";',
        '} catch (Throwable $e) {',
        '    echo "C:", ($e === $second), ":", $e->getMessage(), ":", $e->getLine(), ":", ($e->getPrevious() === null), ":", ($v === 100), ":", $left, ":", $alias, ":", $right, ":", $calls, ";";',
        '} finally { echo "F;"; }',
        '$left = 7;',
        'echo "A:", $left, ":", $alias, ";END;";',
    ]
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'precision-string-mod-carrier': original('%', '05.5tail', 2, carrier=True),
    'precision-string-left-complete': original('<<', '5.5', 384),
    'precision-string-right-leading': original('>>', '2.5tail', 3),
    'precision-string-and-complete': original('&', '5.5', 4),
    'precision-string-or-exponent': original('|', ' +5.5e0 tail', 13),
    'precision-string-xor-complete': original('^', '5.5', 9),
    'precision-string-complete-throw': original('<<', '5.5', 384, throw_at=3),
    'precision-string-leading-warning-throw': original('%', '05.5tail', 2, carrier=True, throw_at=2),
    'precision-string-leading-precision-throw': original('%', '05.5tail', 2, carrier=True, throw_at=3),
}
