<?php
namespace Ns266UntypedGetPeer;
class Leaf266 {
    public function __destruct() {
        echo 'L|';
    }
}
class Middle266 {
    public $pad = true;
    public $edge {
        get {
            echo 'BADMIDDLEGET|';
            return $this->edge;
        }
    }
    public function __construct() {
        $this->edge = $GLOBALS['outside266peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === true ? 'F|' : 'BAD|';
    }
}
class Root266 {
    public $middle {
        get => ($GLOBALS['called266peer'] = true) ? $this->middle : $this->middle;
    }
    public $pad = false {
        get {
            echo 'BADSCALARGET|';
            return $this->pad;
        }
    }
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        $this->middle = new Middle266();
        $this->tail = $GLOBALS['outside266peer'];
    }
    public function __destruct() {
        echo 'D|', Root266::A, '|', 'P|';
        $GLOBALS['member266peer'] = 'B';
    }
}
function &selector266() {
    $receiver266 = new Root266();
    echo 'C|';
    return $receiver266;
}
function member266() {
    echo 'M|', $GLOBALS['called266peer'] === false ? 'N|' : 'BAD|';
    return $GLOBALS['member266peer'];
}
function notice266($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns266UntypedGetPeer\\Root266::A is deprecated' || $message === 'Constant Ns266UntypedGetPeer\\Root266::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member266peer'] = 'A';
    return true;
}
$called266peer = false;
$outside266peer = new Leaf266();
$member266peer = 'A';
\set_error_handler('Ns266UntypedGetPeer\\notice266');
echo 'B|', selector266()::{member266()}, '|Z|';
unset($outside266peer);
echo 'E|';
\restore_error_handler();
