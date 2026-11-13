<?php
namespace Ns285SetBackedClassImplicitPairPeer;
class Leaf285 {
    public function __destruct() {
        echo 'L|';
    }
}
class PadLeaf285 {
    public function __destruct() {
        echo 'U|';
    }
}
class Middle285 {
    public $pad = true;
    public $edge;
    public function __construct() {
        $this->edge = $GLOBALS['outside285peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === true ? 'F|' : 'BAD|';
    }
}
class Root285 {
    public $anchor = 31;
    public $middle;
    public $tail;
    public $pad {
        get => ($GLOBALS['get285peer'] = true) ? 7 : 7;
        set {
            $GLOBALS['set285peer'] = true;
            $this->pad = $value;
        }
    }
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        echo $this->anchor === 31 && $this->pad === 7 && $GLOBALS['get285peer'] === true && $GLOBALS['set285peer'] === false ? 'Q|' : 'BAD|';
        $GLOBALS['get285peer'] = false;
        $this->pad = new PadLeaf285();
        echo $GLOBALS['set285peer'] === true ? 'S|' : 'BAD|';
        $GLOBALS['set285peer'] = false;
        $this->middle = new Middle285();
        $this->tail = $GLOBALS['outside285peer'];
    }
    public function __destruct() {
        echo $this->anchor === 31 ? 'R|' : 'BAD|';
        echo 'D|', Root285::A, '|', 'P|';
        $GLOBALS['member285peer'] = 'B';
    }
}
function &selector285() {
    $receiver285 = new Root285();
    echo 'C|';
    return $receiver285;
}
function member285() {
    echo 'M|', ($GLOBALS['set285peer'] === false && $GLOBALS['get285peer'] === false) ? 'N|' : 'BAD|';
    return $GLOBALS['member285peer'];
}
function notice285($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns285SetBackedClassImplicitPairPeer\\Root285::A is deprecated' || $message === 'Constant Ns285SetBackedClassImplicitPairPeer\\Root285::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member285peer'] = 'A';
    return true;
}
$set285peer = false;
$get285peer = false;
$outside285peer = new Leaf285();
$member285peer = 'A';
\set_error_handler('Ns285SetBackedClassImplicitPairPeer\\notice285');
echo 'B|', selector285()::{member285()}, '|Z|';
unset($outside285peer);
echo 'E|';
\restore_error_handler();
