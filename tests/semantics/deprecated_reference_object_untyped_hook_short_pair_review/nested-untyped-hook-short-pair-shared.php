<?php
namespace Ns277UntypedHookShortPairPeer;
class Leaf277 {
    public function __destruct() {
        echo 'L|';
    }
}
class Middle277 {
    public $pad = true;
    public $edge;
    public function __construct() {
        $this->edge = $GLOBALS['outside277peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === true ? 'F|' : 'BAD|';
    }
}
class Root277 {
    public $pad {
        set => ($GLOBALS['set277peer'] = true) ? $value : $value;
        get {
            $GLOBALS['get277peer'] = true;
            return $this->pad;
        }
    }
    public $middle;
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        echo $this->pad === null && $GLOBALS['get277peer'] === true && $GLOBALS['set277peer'] === false ? 'Q|' : 'BAD|';
        $GLOBALS['get277peer'] = false;
        $this->middle = new Middle277();
        $this->tail = $GLOBALS['outside277peer'];
    }
    public function __destruct() {
        echo 'D|', Root277::A, '|', 'P|';
        $GLOBALS['member277peer'] = 'B';
    }
}
function &selector277() {
    $receiver277 = new Root277();
    echo 'C|';
    return $receiver277;
}
function member277() {
    echo 'M|', ($GLOBALS['set277peer'] === false && $GLOBALS['get277peer'] === false) ? 'N|' : 'BAD|';
    return $GLOBALS['member277peer'];
}
function notice277($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns277UntypedHookShortPairPeer\\Root277::A is deprecated' || $message === 'Constant Ns277UntypedHookShortPairPeer\\Root277::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member277peer'] = 'A';
    return true;
}
$set277peer = false;
$get277peer = false;
$outside277peer = new Leaf277();
$member277peer = 'A';
\set_error_handler('Ns277UntypedHookShortPairPeer\\notice277');
echo 'B|', selector277()::{member277()}, '|Z|';
unset($outside277peer);
echo 'E|';
\restore_error_handler();
