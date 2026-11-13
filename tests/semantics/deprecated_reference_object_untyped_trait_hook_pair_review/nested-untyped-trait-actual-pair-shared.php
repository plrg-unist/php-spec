<?php
namespace Ns280UntypedTraitActualPairPeer;
class Leaf280 {
    public function __destruct() {
        echo 'L|';
    }
}
class Middle280 {
    public $pad = true;
    public $edge;
    public function __construct() {
        $this->edge = $GLOBALS['outside280peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === true ? 'F|' : 'BAD|';
    }
}
trait RootPad280 {
    public $pad {
        set($incoming) => ($GLOBALS['set280peer'] = true) ? $incoming : $incoming;
        get => ($GLOBALS['get280peer'] = true) ? $this->pad : $this->pad;
    }
}
class Root280 {
    use RootPad280;
    public $middle;
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        echo $this->pad === null && $GLOBALS['get280peer'] === true && $GLOBALS['set280peer'] === false ? 'Q|' : 'BAD|';
        $GLOBALS['get280peer'] = false;
        $this->middle = new Middle280();
        $this->tail = $GLOBALS['outside280peer'];
    }
    public function __destruct() {
        echo 'D|', Root280::A, '|', 'P|';
        $GLOBALS['member280peer'] = 'B';
    }
}
function &selector280() {
    $receiver280 = new Root280();
    echo 'C|';
    return $receiver280;
}
function member280() {
    echo 'M|', ($GLOBALS['set280peer'] === false && $GLOBALS['get280peer'] === false) ? 'N|' : 'BAD|';
    return $GLOBALS['member280peer'];
}
function notice280($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns280UntypedTraitActualPairPeer\\Root280::A is deprecated' || $message === 'Constant Ns280UntypedTraitActualPairPeer\\Root280::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member280peer'] = 'A';
    return true;
}
$set280peer = false;
$get280peer = false;
$outside280peer = new Leaf280();
$member280peer = 'A';
\set_error_handler('Ns280UntypedTraitActualPairPeer\\notice280');
echo 'B|', selector280()::{member280()}, '|Z|';
unset($outside280peer);
echo 'E|';
\restore_error_handler();
