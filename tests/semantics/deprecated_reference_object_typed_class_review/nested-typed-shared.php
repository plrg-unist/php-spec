<?php
namespace Ns257TypedClassPeer;
class LeafBase257 {
    public function __destruct() {
        echo 'L|';
    }
}
class LeafChild257 extends LeafBase257 {
}
class Base257 {
    public $pad;
    public LeafBase257 $edge;
}
class Middle257 extends Base257 {
    public function __destruct() {
        echo 'I|', $this->pad === false ? 'F|' : 'BAD|';
        echo $this->edge === $GLOBALS['outside257peer'] ? 'S|' : 'BAD|';
    }
}
class Root257 {
    public Middle257 $middle;
    public LeafBase257 $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', Root257::A, '|';
        $GLOBALS['member257peer'] = 'B';
    }
}
function &selector257() {
    $middle257 = new Middle257();
    $middle257->pad = false;
    $middle257->edge = $GLOBALS['outside257peer'];
    $receiver257 = new Root257();
    $receiver257->middle = $middle257;
    $receiver257->tail = $GLOBALS['outside257peer'];
    echo 'C|';
    return $receiver257;
}
function member257() {
    echo 'M|';
    return $GLOBALS['member257peer'];
}
function notice257($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns257TypedClassPeer\\Root257::A is deprecated' || $message === 'Constant Ns257TypedClassPeer\\Root257::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member257peer'] = 'A';
    return true;
}
$outside257peer = new LeafChild257();
$member257peer = 'A';
\set_error_handler('Ns257TypedClassPeer\\notice257');
echo 'B|', selector257()::{member257()}, '|Z|';
unset($outside257peer);
echo 'E|';
\restore_error_handler();
