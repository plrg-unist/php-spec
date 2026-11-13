<?php
namespace Ns268UntypedShortSetPeer;
class Leaf268 {
    public function __destruct() {
        echo 'L|';
    }
}
class Middle268 {
    public $pad = true {
        set => ($GLOBALS['called268peer'] = true) ? $value : $value;
    }
    public $edge;
    public function __construct() {
        $this->edge = $GLOBALS['outside268peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === true ? 'F|' : 'BAD|';
    }
}
class Root268 {
    public $middle;
    public $pad = false {
        set => ($GLOBALS['called268peer'] = true) ? $value : $value;
    }
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        $this->middle = new Middle268();
        $this->tail = $GLOBALS['outside268peer'];
    }
    public function __destruct() {
        echo 'D|', Root268::A, '|', 'P|';
        $GLOBALS['member268peer'] = 'B';
    }
}
function &selector268() {
    $receiver268 = new Root268();
    echo 'C|';
    return $receiver268;
}
function member268() {
    echo 'M|', $GLOBALS['called268peer'] === false ? 'N|' : 'BAD|';
    return $GLOBALS['member268peer'];
}
function notice268($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns268UntypedShortSetPeer\\Root268::A is deprecated' || $message === 'Constant Ns268UntypedShortSetPeer\\Root268::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member268peer'] = 'A';
    return true;
}
$called268peer = false;
$outside268peer = new Leaf268();
$member268peer = 'A';
\set_error_handler('Ns268UntypedShortSetPeer\\notice268');
echo 'B|', selector268()::{member268()}, '|Z|';
unset($outside268peer);
echo 'E|';
\restore_error_handler();
