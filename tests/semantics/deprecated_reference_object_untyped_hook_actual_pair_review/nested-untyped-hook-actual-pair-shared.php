<?php
namespace Ns279UntypedHookActualPairPeer;
class Leaf279 {
    public function __destruct() {
        echo 'L|';
    }
}
class Middle279 {
    public $pad = true;
    public $edge;
    public function __construct() {
        $this->edge = $GLOBALS['outside279peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === true ? 'F|' : 'BAD|';
    }
}
class Root279 {
    public $pad {
        set($incoming) => ($GLOBALS['set279peer'] = true) ? $incoming : $incoming;
        get => ($GLOBALS['get279peer'] = true) ? $this->pad : $this->pad;
    }
    public $middle;
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        echo $this->pad === null && $GLOBALS['get279peer'] === true && $GLOBALS['set279peer'] === false ? 'Q|' : 'BAD|';
        $GLOBALS['get279peer'] = false;
        $this->middle = new Middle279();
        $this->tail = $GLOBALS['outside279peer'];
    }
    public function __destruct() {
        echo 'D|', Root279::A, '|', 'P|';
        $GLOBALS['member279peer'] = 'B';
    }
}
function &selector279() {
    $receiver279 = new Root279();
    echo 'C|';
    return $receiver279;
}
function member279() {
    echo 'M|', ($GLOBALS['set279peer'] === false && $GLOBALS['get279peer'] === false) ? 'N|' : 'BAD|';
    return $GLOBALS['member279peer'];
}
function notice279($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns279UntypedHookActualPairPeer\\Root279::A is deprecated' || $message === 'Constant Ns279UntypedHookActualPairPeer\\Root279::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member279peer'] = 'A';
    return true;
}
$set279peer = false;
$get279peer = false;
$outside279peer = new Leaf279();
$member279peer = 'A';
\set_error_handler('Ns279UntypedHookActualPairPeer\\notice279');
echo 'B|', selector279()::{member279()}, '|Z|';
unset($outside279peer);
echo 'E|';
\restore_error_handler();
