<?php
namespace Ns254TypedNull;
class Leaf254 {
    public function __destruct() {
        echo 'L|';
    }
}
class Base254 {
    public null $tag;
}
class Middle254 extends Base254 {
    public $edge;
    public function __destruct() {
        echo 'I|', $this->tag === null ? 'N|' : 'BAD|';
    }
}
class Root254 {
    public $middle;
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', Root254::A, '|';
        $GLOBALS['member254peer'] = 'B';
    }
}
function &selector254() {
    $middle254 = new Middle254();
    $middle254->tag = null;
    $middle254->edge = $GLOBALS['outside254peer'];
    $receiver254 = new Root254();
    $receiver254->middle = $middle254;
    $receiver254->tail = $GLOBALS['outside254peer'];
    echo 'C|';
    return $receiver254;
}
function member254() {
    echo 'M|';
    return $GLOBALS['member254peer'];
}
function notice254($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns254TypedNull\\Root254::A is deprecated' || $message === 'Constant Ns254TypedNull\\Root254::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member254peer'] = 'A';
    return true;
}
$outside254peer = new Leaf254();
$member254peer = 'A';
\set_error_handler('Ns254TypedNull\\notice254');
echo 'B|', selector254()::{member254()}, '|Z|';
unset($outside254peer);
echo 'E|';
\restore_error_handler();
