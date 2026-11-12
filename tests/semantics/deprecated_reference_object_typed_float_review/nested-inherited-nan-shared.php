<?php
namespace Ns249TypedFloat;
class Leaf249 {
    public function __destruct() {
        echo 'L|';
    }
}
class Base249 {
    public float $tag;
}
class Middle249 extends Base249 {
    public $edge;
    public function __destruct() {
        echo 'I|', $this->tag !== $this->tag ? 'N|' : 'BAD|';
    }
}
class Root249 {
    public $middle;
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', Root249::A, '|';
        $GLOBALS['member249peer'] = 'B';
    }
}
function &selector249() {
    $middle249 = new Middle249();
    $middle249->tag = NAN;
    $middle249->edge = $GLOBALS['outside249peer'];
    $receiver249 = new Root249();
    $receiver249->middle = $middle249;
    $receiver249->tail = $GLOBALS['outside249peer'];
    echo 'C|';
    return $receiver249;
}
function member249() {
    echo 'M|';
    return $GLOBALS['member249peer'];
}
function notice249($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns249TypedFloat\\Root249::A is deprecated' || $message === 'Constant Ns249TypedFloat\\Root249::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member249peer'] = 'A';
    return true;
}
$outside249peer = new Leaf249();
$member249peer = 'A';
\set_error_handler('Ns249TypedFloat\\notice249');
echo 'B|', selector249()::{member249()}, '|Z|';
unset($outside249peer);
echo 'E|';
\restore_error_handler();
