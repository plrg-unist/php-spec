<?php
namespace Ns264HookPeer;
class Leaf264 {
    public function __destruct() {
        echo 'L|';
    }
}
class Middle264 {
    public bool $pad = true;
    public Leaf264 $edge {
        get {
            echo 'BADMIDDLEGET|';
            return $this->edge;
        }
    }
    public function __construct() {
        $this->edge = $GLOBALS['outside264peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === true ? 'F|' : 'BAD|';
    }
}
class Root264 {
    public Middle264 $middle {
        get {
            echo 'BADROOTGET|';
            return $this->middle;
        }
    }
    public bool $pad = false;
    public Leaf264 $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        $this->middle = new Middle264();
        $this->tail = $GLOBALS['outside264peer'];
    }
    public function __destruct() {
        echo 'D|', Root264::A, '|', $this->pad === false ? 'P|' : 'BAD|';
        $GLOBALS['member264peer'] = 'B';
    }
}
function &selector264() {
    $receiver264 = new Root264();
    echo 'C|';
    return $receiver264;
}
function member264() {
    echo 'M|';
    return $GLOBALS['member264peer'];
}
function notice264($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns264HookPeer\\Root264::A is deprecated' || $message === 'Constant Ns264HookPeer\\Root264::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member264peer'] = 'A';
    return true;
}
$outside264peer = new Leaf264();
$member264peer = 'A';
\set_error_handler('Ns264HookPeer\\notice264');
echo 'B|', selector264()::{member264()}, '|Z|';
unset($outside264peer);
echo 'E|';
\restore_error_handler();
