<?php
namespace Ns267UntypedSetPeer;
class Leaf267 {
    public function __destruct() {
        echo 'L|';
    }
}
class Middle267 {
    public $pad = true {
        set {
            $GLOBALS['called267peer'] = true;
            $this->pad = $value;
        }
    }
    public $edge;
    public function __construct() {
        $this->edge = $GLOBALS['outside267peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === true ? 'F|' : 'BAD|';
    }
}
class Root267 {
    public $middle;
    public $pad = false {
        set {
            $GLOBALS['called267peer'] = true;
            $this->pad = $value;
        }
    }
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        $this->middle = new Middle267();
        $this->tail = $GLOBALS['outside267peer'];
    }
    public function __destruct() {
        echo 'D|', Root267::A, '|', 'P|';
        $GLOBALS['member267peer'] = 'B';
    }
}
function &selector267() {
    $receiver267 = new Root267();
    echo 'C|';
    return $receiver267;
}
function member267() {
    echo 'M|', $GLOBALS['called267peer'] === false ? 'N|' : 'BAD|';
    return $GLOBALS['member267peer'];
}
function notice267($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns267UntypedSetPeer\\Root267::A is deprecated' || $message === 'Constant Ns267UntypedSetPeer\\Root267::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member267peer'] = 'A';
    return true;
}
$called267peer = false;
$outside267peer = new Leaf267();
$member267peer = 'A';
\set_error_handler('Ns267UntypedSetPeer\\notice267');
echo 'B|', selector267()::{member267()}, '|Z|';
unset($outside267peer);
echo 'E|';
\restore_error_handler();
