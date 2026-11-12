<?php
namespace Ns247NestedString;
class Leaf247 {
    public function __destruct() {
        echo 'L|';
    }
}
class Middle247 {
    public $tag;
    public $edge;
    public function __destruct() {
        echo 'I|', $this->tag === 'tag' ? 'S|' : 'BAD|';
    }
}
class Root247 {
    public $middle;
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', Root247::A, '|';
        $GLOBALS['member247peer'] = 'B';
    }
}
function &selector247() {
    $prefix247 = 'ta';
    $middle247 = new Middle247();
    $middle247->tag = $prefix247 . 'g';
    $middle247->edge = $GLOBALS['outside247peer'];
    $receiver247 = new Root247();
    $receiver247->middle = $middle247;
    $receiver247->tail = $GLOBALS['outside247peer'];
    echo 'C|';
    return $receiver247;
}
function member247() {
    echo 'M|';
    return $GLOBALS['member247peer'];
}
function notice247($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns247NestedString\\Root247::A is deprecated' || $message === 'Constant Ns247NestedString\\Root247::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member247peer'] = 'A';
    return true;
}
$outside247peer = new Leaf247();
$member247peer = 'A';
\set_error_handler('Ns247NestedString\\notice247');
echo 'B|', selector247()::{member247()}, '|Z|';
unset($outside247peer);
echo 'E|';
\restore_error_handler();
