<?php
namespace Ns275UntypedHookPairPeer;
class Leaf275 {
    public function __destruct() {
        echo 'L|';
    }
}
class Middle275 {
    public $pad = true;
    public $edge;
    public function __construct() {
        $this->edge = $GLOBALS['outside275peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === true ? 'F|' : 'BAD|';
    }
}
class Root275 {
    public $pad = false {
        set {
            $GLOBALS['set275peer'] = true;
            $this->pad = $value;
        }
        get {
            $GLOBALS['get275peer'] = true;
            return $this->pad;
        }
    }
    public $middle;
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        $this->middle = new Middle275();
        $this->tail = $GLOBALS['outside275peer'];
    }
    public function __destruct() {
        echo 'D|', Root275::A, '|', 'P|';
        $GLOBALS['member275peer'] = 'B';
    }
}
function &selector275() {
    $receiver275 = new Root275();
    echo 'C|';
    return $receiver275;
}
function member275() {
    echo 'M|', ($GLOBALS['set275peer'] === false && $GLOBALS['get275peer'] === false) ? 'N|' : 'BAD|';
    return $GLOBALS['member275peer'];
}
function notice275($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns275UntypedHookPairPeer\\Root275::A is deprecated' || $message === 'Constant Ns275UntypedHookPairPeer\\Root275::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member275peer'] = 'A';
    return true;
}
$set275peer = false;
$get275peer = false;
$outside275peer = new Leaf275();
$member275peer = 'A';
\set_error_handler('Ns275UntypedHookPairPeer\\notice275');
echo 'B|', selector275()::{member275()}, '|Z|';
unset($outside275peer);
echo 'E|';
\restore_error_handler();
