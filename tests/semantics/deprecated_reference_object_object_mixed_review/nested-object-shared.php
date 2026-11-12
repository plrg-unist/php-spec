<?php
namespace Ns259ObjectMixedPeer;
class LeafBase259 {
    public function __destruct() {
        echo 'L|';
    }
}
class LeafChild259 extends LeafBase259 {
}
class Base259 {
    public $pad;
    public int|object|string $edge;
}
class Middle259 extends Base259 {
    public function __destruct() {
        echo 'I|', $this->pad === false ? 'F|' : 'BAD|';
        echo $this->edge === $GLOBALS['outside259peer'] ? 'S|' : 'BAD|';
    }
}
class Root259 {
    public false|object $middle;
    public ?object $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', Root259::A, '|';
        $GLOBALS['member259peer'] = 'B';
    }
}
function &selector259() {
    $middle259 = new Middle259();
    $middle259->pad = false;
    $middle259->edge = $GLOBALS['outside259peer'];
    $receiver259 = new Root259();
    $receiver259->middle = $middle259;
    $receiver259->tail = $GLOBALS['outside259peer'];
    echo 'C|';
    return $receiver259;
}
function member259() {
    echo 'M|';
    return $GLOBALS['member259peer'];
}
function notice259($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns259ObjectMixedPeer\\Root259::A is deprecated' || $message === 'Constant Ns259ObjectMixedPeer\\Root259::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member259peer'] = 'A';
    return true;
}
$outside259peer = new LeafChild259();
$member259peer = 'A';
\set_error_handler('Ns259ObjectMixedPeer\\notice259');
echo 'B|', selector259()::{member259()}, '|Z|';
unset($outside259peer);
echo 'E|';
\restore_error_handler();
