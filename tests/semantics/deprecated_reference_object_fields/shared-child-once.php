<?php
namespace Ns243SharedChild;
class Shared243 {
    public function __destruct() {
        echo 'S|';
        $GLOBALS['released243'] = true;
        $GLOBALS['member243'] = 'B';
    }
}
class Between243 {
    public function __destruct() {
        echo $GLOBALS['released243'] ? 'T1|' : 'T0|';
    }
}
class Base243 {
    public $head, $middle;
    #[\Deprecated]
    public const A = 7, B = 8;
    public function __destruct() {
        echo 'D|', Child243::A, '|';
    }
}
class Child243 extends Base243 {
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
}
function &selector243() {
    $shared243 = new Shared243();
    $receiver243 = new Child243();
    $receiver243->tail = $shared243;
    $receiver243->middle = new Between243();
    $receiver243->head = $shared243;
    unset($shared243);
    echo 'C|';
    return $receiver243;
}
function member243() {
    echo 'M|';
    return $GLOBALS['member243'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns243SharedChild\\Child243::A is deprecated' || $message === 'Constant Ns243SharedChild\\Child243::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member243'] = 'A';
    return true;
});
$released243 = false;
$member243 = 'A';
echo 'B|', selector243()::{member243()}, '|Z|';
\restore_error_handler();
