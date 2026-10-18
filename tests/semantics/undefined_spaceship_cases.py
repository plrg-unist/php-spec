"""Undefined scalar spaceship reads retain NULL across real warning callbacks."""

CASES = {
    'scalar-tags-and-frozen-known-left': b'''<?php
function scalarTags89($n, $m, $file, $line) { $GLOBALS['x'] = 9; return true; }
set_error_handler('scalarTags89');
echo 'B|';
$right = null; echo $x <=> $right, ':'; unset($x);
$right = false; echo $x <=> $right, ':'; unset($x);
$right = true; echo $x <=> $right, ':'; unset($x);
$right = 0; echo $x <=> $right, ':'; unset($x);
$right = 1.5; echo $x <=> $right, ':'; unset($x);
$right = NAN; echo $x <=> $right, ':'; unset($x);
$right = '0'; echo $x <=> $right, ':'; unset($x);
$part = 'value'; $right = $part . '0'; echo $x <=> $right, ':'; unset($x);
echo null <=> $x, ':'; unset($x);
echo false <=> $x, ':'; unset($x);
echo true <=> $x, ':'; unset($x);
echo 0 <=> $x, ':'; unset($x);
echo 1.5 <=> $x, ':'; unset($x);
echo NAN <=> $x, ':'; unset($x);
echo '0' <=> $x, ':'; unset($x);
echo ($part . '0') <=> $x, ';END;';
''',
    'both-missing-boundary': b'''<?php
function scalarBoth89($n, $m, $file, $line) { echo 'H|'; return true; }
set_error_handler('scalarBoth89');
echo 'B|'; $result = $left <=> $right; echo $result;
''',
    'callback-array-boundary': b'''<?php
function scalarArray89($n, $m, $file, $line) { echo 'H|'; $GLOBALS['x'] = 9; $GLOBALS['right'] = []; return true; }
$right = 1;
set_error_handler('scalarArray89');
echo 'B|'; $result = $x <=> $right; echo $result;
''',
    'missing-left-constant': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", $line, ":", ($m === 'Undefined variable $x'), ";";
    $GLOBALS['x'] = 9;
    $GLOBALS['y'] = 0;
    return true;
}
$y = 2;
set_error_handler('h');
$v = $x <=> 1;
echo "R:", $v, ":", ($v === -1), ":", $x, ":", $y, ";END;";
''',
    'missing-right-constant': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", $line, ":", ($m === 'Undefined variable $x'), ";";
    $GLOBALS['x'] = 9;
    $GLOBALS['y'] = 0;
    return true;
}
$y = 2;
set_error_handler('h');
$v = 1 <=> $x;
echo "R:", $v, ":", ($v === 1), ":", $x, ":", $y, ";END;";
''',
    'missing-left-cv': b'''<?php
function h($n, $m, $file, $line) {
    echo "H:", $n, ":", $line, ":", ($m === 'Undefined variable $x'), ";";
    $GLOBALS['x'] = 9;
    $GLOBALS['y'] = 0;
    return true;
}
$y = 2;
set_error_handler('h');
$v = $x <=> $y;
echo "R:", $v, ":", ($v === 0), ":", $x, ":", $y, ";END;";
''',
}
