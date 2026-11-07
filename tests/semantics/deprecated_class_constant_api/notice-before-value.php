<?php
$entered = false;
function notice213($level, $message) {
    echo 'C|';
    if (!$GLOBALS['entered']) {
        $GLOBALS['entered'] = true;
        \define('SEED213', 9);
        echo 'I|', Child213::C, '|';
    }
    return true;
}
class Base213 { #[\Deprecated] public const C = \SEED213; }
class Child213 extends Base213 {}
\set_error_handler('notice213');
$outer = \constant('Child213::C');
echo 'O|', $outer, '|';
$again = Child213::C;
echo 'R|', $again, '|Z|';
