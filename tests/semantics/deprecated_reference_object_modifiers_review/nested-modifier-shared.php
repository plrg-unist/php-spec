<?php
namespace Ns263ModifierPeer;
class LeafBase263 {
    public function __destruct() {
        echo 'L|';
    }
}
class LeafChild263 extends LeafBase263 {
}
readonly class Base263 {
    protected protected(set) bool $pad;
    private private(set) LeafBase263 $edge;
    public function __construct() {
        $this->pad = false;
        $this->edge = $GLOBALS['outside263peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === false ? 'F|' : 'BAD|';
        echo $this->edge === $GLOBALS['outside263peer'] ? 'S|' : 'BAD|';
    }
}
readonly class Middle263 extends Base263 {
}
class Root263 {
    protected private(set) Middle263 $middle;
    private private(set) readonly LeafBase263 $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        $this->middle = new Middle263();
        $this->tail = $GLOBALS['outside263peer'];
    }
    public function __destruct() {
        echo 'D|', Root263::A, '|';
        echo $this->tail === $GLOBALS['outside263peer'] ? 'T|' : 'BAD|';
        $GLOBALS['member263peer'] = 'B';
    }
}
function &selector263() {
    $receiver263 = new Root263();
    echo 'C|';
    return $receiver263;
}
function member263() {
    echo 'M|';
    return $GLOBALS['member263peer'];
}
function notice263($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns263ModifierPeer\\Root263::A is deprecated' || $message === 'Constant Ns263ModifierPeer\\Root263::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member263peer'] = 'A';
    return true;
}
$outside263peer = new LeafChild263();
$member263peer = 'A';
\set_error_handler('Ns263ModifierPeer\\notice263');
echo 'B|', selector263()::{member263()}, '|Z|';
unset($outside263peer);
echo 'E|';
\restore_error_handler();
