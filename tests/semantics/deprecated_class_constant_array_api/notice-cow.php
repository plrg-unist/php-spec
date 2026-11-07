<?php
$entered = false;
function notice214($level, $message) {
    echo 'H|';
    if (!$GLOBALS['entered']) {
        $GLOBALS['entered'] = true;
        $copy = Child214::TREE;
        $copy[0] = 9;
        $copy[1][0] = 8;
        echo 'I|', $copy[0], '|', $copy[1][0], '|';
        $original = Child214::TREE;
        echo $original[0], '|', $original[1][0], '|';
    }
    return true;
}
class Base214 { #[\Deprecated] public const TREE = [1, [2]]; }
class Child214 extends Base214 {}
\set_error_handler('notice214');
$value = \constant('Child214::TREE');
echo 'O|', $value[0], '|', $value[1][0], '|';
$value[0] = 4;
$value[1][0] = 5;
echo 'M|', $value[0], '|', $value[1][0], '|';
$again = \constant('Base214::TREE');
echo 'R|', $again[0], '|', $again[1][0], '|Z|';
