<?php
namespace Ns252TypedFalse;
class Leaf252 {
    public function __destruct() {
        echo 'L|';
    }
}
class Base252 {
    public false $tag;
}
class Middle252 extends Base252 {
    public $edge;
    public function __destruct() {
        echo 'I|', $this->tag === false ? 'F|' : 'BAD|';
    }
}
class Root252 {
    public $middle;
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', Root252::A, '|';
        $GLOBALS['member252peer'] = 'B';
    }
}
function &selector252() {
    $middle252 = new Middle252();
    $middle252->tag = false;
    $middle252->edge = $GLOBALS['outside252peer'];
    $receiver252 = new Root252();
    $receiver252->middle = $middle252;
    $receiver252->tail = $GLOBALS['outside252peer'];
    echo 'C|';
    return $receiver252;
}
function member252() {
    echo 'M|';
    return $GLOBALS['member252peer'];
}
function notice252($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns252TypedFalse\\Root252::A is deprecated' || $message === 'Constant Ns252TypedFalse\\Root252::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member252peer'] = 'A';
    return true;
}
$outside252peer = new Leaf252();
$member252peer = 'A';
\set_error_handler('Ns252TypedFalse\\notice252');
echo 'B|', selector252()::{member252()}, '|Z|';
unset($outside252peer);
echo 'E|';
\restore_error_handler();
