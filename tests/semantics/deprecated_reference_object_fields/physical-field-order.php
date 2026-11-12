<?php
namespace Ns243FieldOrder;
class Left243 {
    public function __destruct() {
        echo 'L|';
        $GLOBALS['member243'] = 'B';
    }
}
class Right243 {
    public function __destruct() {
        echo 'R|';
        $GLOBALS['member243'] = 'C';
    }
}
class Base243 {
    public $head, $tag, $empty;
    #[\Deprecated]
    public const A = 6, B = 7, C = 8;
    public function __destruct() {
        echo 'D|', Child243::A, '|';
    }
}
class Child243 extends Base243 {
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10, C = 11;
}
function &selector243() {
    $receiver243 = new Child243();
    $receiver243->tail = new Right243();
    $receiver243->head = new Left243();
    $receiver243->tag = 0;
    echo 'C|';
    return $receiver243;
}
function member243() {
    echo 'M|';
    return $GLOBALS['member243'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns243FieldOrder\\Child243::A is deprecated' || $message === 'Constant Ns243FieldOrder\\Child243::C is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member243'] = 'A';
    return true;
});
$member243 = 'A';
echo 'B|', selector243()::{member243()}, '|Z|';
\restore_error_handler();
