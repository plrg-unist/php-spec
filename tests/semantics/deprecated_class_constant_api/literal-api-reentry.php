<?php
$entered = false;
function noticeRec213($level, $message) {
    echo 'L|';
    if (!$GLOBALS['entered']) {
        $GLOBALS['entered'] = true;
        \define('INNERSEED213', 9);
        echo 'A|', \constant('BaseRec213::C'), '|';
    }
    return true;
}
class BaseRec213 { #[\Deprecated] public const C = \INNERSEED213; }
class ChildRec213 extends BaseRec213 {}
\set_error_handler('noticeRec213');
$outer = ChildRec213::C;
echo 'O|', $outer, '|';
$again = \constant('ChildRec213::C');
echo 'R|', $again, '|Z|';
