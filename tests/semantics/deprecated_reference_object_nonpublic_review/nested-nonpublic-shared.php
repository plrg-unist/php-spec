<?php
namespace Ns262NonpublicPeer;
class LeafBase262 {
    public function __destruct() {
        echo 'L|';
    }
}
class LeafChild262 extends LeafBase262 {
}
class Base262 {
    protected bool $pad = false;
    private LeafBase262 $edge;
    public function __construct() {
        $this->pad = false;
        $this->edge = $GLOBALS['outside262peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === false ? 'F|' : 'BAD|';
        echo $this->edge === $GLOBALS['outside262peer'] ? 'S|' : 'BAD|';
    }
}
class Middle262 extends Base262 {
}
class Root262 {
    protected Middle262 $middle;
    private LeafBase262 $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        $this->middle = new Middle262();
        $this->tail = $GLOBALS['outside262peer'];
    }
    public function __destruct() {
        echo 'D|', Root262::A, '|';
        echo $this->tail === $GLOBALS['outside262peer'] ? 'T|' : 'BAD|';
        $GLOBALS['member262peer'] = 'B';
    }
}
function &selector262() {
    $receiver262 = new Root262();
    echo 'C|';
    return $receiver262;
}
function member262() {
    echo 'M|';
    return $GLOBALS['member262peer'];
}
function notice262($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns262NonpublicPeer\\Root262::A is deprecated' || $message === 'Constant Ns262NonpublicPeer\\Root262::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member262peer'] = 'A';
    return true;
}
$outside262peer = new LeafChild262();
$member262peer = 'A';
\set_error_handler('Ns262NonpublicPeer\\notice262');
echo 'B|', selector262()::{member262()}, '|Z|';
unset($outside262peer);
echo 'E|';
\restore_error_handler();
