<?php
namespace Ns248TypedString;
class Leaf248 {
    public function __destruct() {
        echo 'L|';
    }
}
class Base248 {
    public string $tag;
}
class Middle248 extends Base248 {
    public $edge;
    public function __destruct() {
        echo 'I|', $this->tag === 'tag' ? 'S|' : 'BAD|';
    }
}
class Root248 {
    public $middle;
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', Root248::A, '|';
        $GLOBALS['member248peer'] = 'B';
    }
}
function &selector248() {
    $prefix248 = 'ta';
    $middle248 = new Middle248();
    $middle248->tag = $prefix248 . 'g';
    $middle248->edge = $GLOBALS['outside248peer'];
    $receiver248 = new Root248();
    $receiver248->middle = $middle248;
    $receiver248->tail = $GLOBALS['outside248peer'];
    echo 'C|';
    return $receiver248;
}
function member248() {
    echo 'M|';
    return $GLOBALS['member248peer'];
}
function notice248($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns248TypedString\\Root248::A is deprecated' || $message === 'Constant Ns248TypedString\\Root248::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member248peer'] = 'A';
    return true;
}
$outside248peer = new Leaf248();
$member248peer = 'A';
\set_error_handler('Ns248TypedString\\notice248');
echo 'B|', selector248()::{member248()}, '|Z|';
unset($outside248peer);
echo 'E|';
\restore_error_handler();
