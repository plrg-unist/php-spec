"""A quiet negative-zero copy survives final power callback origin removal."""

CASES = {
    'quiet-power-copy-negative-zero-default': b'''<?php
function h($n, $m, $file, $line) {
    $GLOBALS['calls'] = $GLOBALS['calls'] + 1;
    echo 'H:', $GLOBALS['calls'], ':', $n, ':', $line, ':', $m === 'Power of base 0 and negative exponent is deprecated', ':', ($GLOBALS['left'] === '-0.0' && $GLOBALS['right'] === -3), ';';
    if ($GLOBALS['calls'] !== 1 || $n !== 8192 || $line !== 25 || $m !== 'Power of base 0 and negative exponent is deprecated') { echo 'BAD-H;'; return true; }
    unset($GLOBALS['left'], $GLOBALS['right']);
    return false;
}
set_error_handler('h', 8192);
$calls = 0; $pick = true; $tail = '0.0';
$left = '-' . $tail; $right = -3; $v = 100;










try {
    $v = (($pick ? $left : 7)
        **
        $right);
    echo 'R:', $v, ':', $v === -1e999, ':', !isset($left), ':', !isset($right), ':', $calls === 1, ';';
} catch (Throwable $e) { echo 'BAD-E:', $e->getMessage(), ';'; }
finally { echo 'F;'; }
$left = 7; $right = 8;
echo 'A:', $left === 7, ':', $right === 8, ':', $calls === 1, ';END;';
''',
}
