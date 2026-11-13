<?php
namespace Ns261ReadonlyPeer;
class LeafBase261 {
    public function __destruct() {
        echo 'L|';
    }
}
class LeafChild261 extends LeafBase261 {
}
readonly class Base261 {
    public bool $pad;
    public LeafBase261 $edge;
    public function __construct() {
        $this->pad = false;
        $this->edge = $GLOBALS['outside261peer'];
    }
}
readonly class Middle261 extends Base261 {
    public function __destruct() {
        echo 'I|', $this->pad === false ? 'F|' : 'BAD|';
        echo $this->edge === $GLOBALS['outside261peer'] ? 'S|' : 'BAD|';
    }
}
class Root261 {
    public readonly Middle261 $middle;
    public readonly LeafBase261 $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        $this->middle = new Middle261();
        $this->tail = $GLOBALS['outside261peer'];
    }
    public function __destruct() {
        echo 'D|', Root261::A, '|';
        $GLOBALS['member261peer'] = 'B';
    }
}
function &selector261() {
    $receiver261 = new Root261();
    echo 'C|';
    return $receiver261;
}
function member261() {
    echo 'M|';
    return $GLOBALS['member261peer'];
}
function notice261($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns261ReadonlyPeer\\Root261::A is deprecated' || $message === 'Constant Ns261ReadonlyPeer\\Root261::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member261peer'] = 'A';
    return true;
}
$outside261peer = new LeafChild261();
$member261peer = 'A';
\set_error_handler('Ns261ReadonlyPeer\\notice261');
echo 'B|', selector261()::{member261()}, '|Z|';
unset($outside261peer);
echo 'E|';
\restore_error_handler();
