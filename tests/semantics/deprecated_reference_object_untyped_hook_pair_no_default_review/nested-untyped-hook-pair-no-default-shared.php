<?php
namespace Ns276UntypedHookPairNoDefaultPeer;
class Leaf276 {
    public function __destruct() {
        echo 'L|';
    }
}
class Middle276 {
    public $pad = true;
    public $edge;
    public function __construct() {
        $this->edge = $GLOBALS['outside276peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === true ? 'F|' : 'BAD|';
    }
}
class Root276 {
    public $pad {
        set {
            $GLOBALS['set276peer'] = true;
            $this->pad = $value;
        }
        get {
            $GLOBALS['get276peer'] = true;
            return $this->pad;
        }
    }
    public $middle;
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        echo $this->pad === null && $GLOBALS['get276peer'] === true && $GLOBALS['set276peer'] === false ? 'Q|' : 'BAD|';
        $GLOBALS['get276peer'] = false;
        $this->middle = new Middle276();
        $this->tail = $GLOBALS['outside276peer'];
    }
    public function __destruct() {
        echo 'D|', Root276::A, '|', 'P|';
        $GLOBALS['member276peer'] = 'B';
    }
}
function &selector276() {
    $receiver276 = new Root276();
    echo 'C|';
    return $receiver276;
}
function member276() {
    echo 'M|', ($GLOBALS['set276peer'] === false && $GLOBALS['get276peer'] === false) ? 'N|' : 'BAD|';
    return $GLOBALS['member276peer'];
}
function notice276($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns276UntypedHookPairNoDefaultPeer\\Root276::A is deprecated' || $message === 'Constant Ns276UntypedHookPairNoDefaultPeer\\Root276::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member276peer'] = 'A';
    return true;
}
$set276peer = false;
$get276peer = false;
$outside276peer = new Leaf276();
$member276peer = 'A';
\set_error_handler('Ns276UntypedHookPairNoDefaultPeer\\notice276');
echo 'B|', selector276()::{member276()}, '|Z|';
unset($outside276peer);
echo 'E|';
\restore_error_handler();
