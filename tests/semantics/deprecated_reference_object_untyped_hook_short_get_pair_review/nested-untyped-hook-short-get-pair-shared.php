<?php
namespace Ns278UntypedHookShortGetPairPeer;
class Leaf278 {
    public function __destruct() {
        echo 'L|';
    }
}
class Middle278 {
    public $pad = true;
    public $edge;
    public function __construct() {
        $this->edge = $GLOBALS['outside278peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === true ? 'F|' : 'BAD|';
    }
}
class Root278 {
    public $pad {
        set {
            $GLOBALS['set278peer'] = true;
            $this->pad = $value;
        }
        get => ($GLOBALS['get278peer'] = true) ? $this->pad : $this->pad;
    }
    public $middle;
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        echo $this->pad === null && $GLOBALS['get278peer'] === true && $GLOBALS['set278peer'] === false ? 'Q|' : 'BAD|';
        $GLOBALS['get278peer'] = false;
        $this->middle = new Middle278();
        $this->tail = $GLOBALS['outside278peer'];
    }
    public function __destruct() {
        echo 'D|', Root278::A, '|', 'P|';
        $GLOBALS['member278peer'] = 'B';
    }
}
function &selector278() {
    $receiver278 = new Root278();
    echo 'C|';
    return $receiver278;
}
function member278() {
    echo 'M|', ($GLOBALS['set278peer'] === false && $GLOBALS['get278peer'] === false) ? 'N|' : 'BAD|';
    return $GLOBALS['member278peer'];
}
function notice278($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns278UntypedHookShortGetPairPeer\\Root278::A is deprecated' || $message === 'Constant Ns278UntypedHookShortGetPairPeer\\Root278::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member278peer'] = 'A';
    return true;
}
$set278peer = false;
$get278peer = false;
$outside278peer = new Leaf278();
$member278peer = 'A';
\set_error_handler('Ns278UntypedHookShortGetPairPeer\\notice278');
echo 'B|', selector278()::{member278()}, '|Z|';
unset($outside278peer);
echo 'E|';
\restore_error_handler();
