<?php
namespace Ns288SameNameParentClassImplicitPairPeer;
class Leaf288 {
    public function __destruct() {
        echo 'L|';
    }
}
class PadLeaf288 {
    public function __destruct() {
        echo 'U|';
    }
}
class Middle288 {
    public $pad = true;
    public $edge;
    public function __construct() {
        $this->edge = $GLOBALS['outside288peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === true ? 'F|' : 'BAD|';
    }
}
class Parent288 {
    public $anchor = 31;
    public $pad = 99;
}
class Root288 extends Parent288 {
    public $middle;
    public $tail;
    public $pad {
        set => ($GLOBALS['set288peer'] = true) ? $value : $value;
        get {
            $GLOBALS['get288peer'] = true;
            return 7;
        }
    }
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        echo $this->anchor === 31 && $this->pad === 7 && $GLOBALS['get288peer'] === true && $GLOBALS['set288peer'] === false ? 'Q|' : 'BAD|';
        $GLOBALS['get288peer'] = false;
        $this->pad = new PadLeaf288();
        echo $GLOBALS['set288peer'] === true ? 'S|' : 'BAD|';
        $GLOBALS['set288peer'] = false;
        $this->middle = new Middle288();
        $this->tail = $GLOBALS['outside288peer'];
    }
    public function __destruct() {
        echo $this->anchor === 31 ? 'R|' : 'BAD|';
        echo 'D|', Root288::A, '|', 'P|';
        $GLOBALS['member288peer'] = 'B';
    }
}
function &selector288() {
    $receiver288 = new Root288();
    echo 'C|';
    return $receiver288;
}
function member288() {
    echo 'M|', ($GLOBALS['set288peer'] === false && $GLOBALS['get288peer'] === false) ? 'N|' : 'BAD|';
    return $GLOBALS['member288peer'];
}
function notice288($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns288SameNameParentClassImplicitPairPeer\\Root288::A is deprecated' || $message === 'Constant Ns288SameNameParentClassImplicitPairPeer\\Root288::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member288peer'] = 'A';
    return true;
}
$set288peer = false;
$get288peer = false;
$outside288peer = new Leaf288();
$member288peer = 'A';
\set_error_handler('Ns288SameNameParentClassImplicitPairPeer\\notice288');
echo 'B|', selector288()::{member288()}, '|Z|';
unset($outside288peer);
echo 'E|';
\restore_error_handler();
