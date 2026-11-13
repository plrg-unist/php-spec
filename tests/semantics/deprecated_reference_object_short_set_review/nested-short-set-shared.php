<?php
namespace Ns265ShortSetPeer;
class Leaf265 {
    public function __destruct() {
        echo 'L|';
    }
}
class Middle265 {
    public bool $pad = false {
        set => $GLOBALS['called265peer'] = true;
    }
    public Leaf265 $edge {
        get {
            echo 'BADMIDDLEGET|';
            return $this->edge;
        }
    }
    public function __construct() {
        $this->edge = $GLOBALS['outside265peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === false ? 'F|' : 'BAD|';
    }
}
class Root265 {
    public Middle265 $middle {
        get {
            echo 'BADROOTGET|';
            return $this->middle;
        }
    }
    public bool $pad = false;
    public Leaf265 $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        $this->middle = new Middle265();
        $this->tail = $GLOBALS['outside265peer'];
    }
    public function __destruct() {
        echo 'D|', Root265::A, '|', $this->pad === false ? 'P|' : 'BAD|';
        $GLOBALS['member265peer'] = 'B';
    }
}
function &selector265() {
    $receiver265 = new Root265();
    echo 'C|';
    return $receiver265;
}
function member265() {
    echo 'M|', $GLOBALS['called265peer'] === false ? 'N|' : 'BAD|';
    return $GLOBALS['member265peer'];
}
function notice265($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns265ShortSetPeer\\Root265::A is deprecated' || $message === 'Constant Ns265ShortSetPeer\\Root265::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member265peer'] = 'A';
    return true;
}
$called265peer = false;
$outside265peer = new Leaf265();
$member265peer = 'A';
\set_error_handler('Ns265ShortSetPeer\\notice265');
echo 'B|', selector265()::{member265()}, '|Z|';
unset($outside265peer);
echo 'E|';
\restore_error_handler();
