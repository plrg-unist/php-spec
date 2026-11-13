<?php
namespace Ns287ParentedClassImplicitPairPeer;
class Leaf287 {
    public function __destruct() {
        echo 'L|';
    }
}
class PadLeaf287 {
    public function __destruct() {
        echo 'U|';
    }
}
class Middle287 {
    public $pad = true;
    public $edge;
    public function __construct() {
        $this->edge = $GLOBALS['outside287peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === true ? 'F|' : 'BAD|';
    }
}
class Parent287 {
    public $anchor = 31;
}
class Root287 extends Parent287 {
    public $middle;
    public $tail;
    public $pad {
        set => ($GLOBALS['set287peer'] = true) ? $value : $value;
        get {
            $GLOBALS['get287peer'] = true;
            return 7;
        }
    }
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        echo $this->anchor === 31 && $this->pad === 7 && $GLOBALS['get287peer'] === true && $GLOBALS['set287peer'] === false ? 'Q|' : 'BAD|';
        $GLOBALS['get287peer'] = false;
        $this->pad = new PadLeaf287();
        echo $GLOBALS['set287peer'] === true ? 'S|' : 'BAD|';
        $GLOBALS['set287peer'] = false;
        $this->middle = new Middle287();
        $this->tail = $GLOBALS['outside287peer'];
    }
    public function __destruct() {
        echo $this->anchor === 31 ? 'R|' : 'BAD|';
        echo 'D|', Root287::A, '|', 'P|';
        $GLOBALS['member287peer'] = 'B';
    }
}
function &selector287() {
    $receiver287 = new Root287();
    echo 'C|';
    return $receiver287;
}
function member287() {
    echo 'M|', ($GLOBALS['set287peer'] === false && $GLOBALS['get287peer'] === false) ? 'N|' : 'BAD|';
    return $GLOBALS['member287peer'];
}
function notice287($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns287ParentedClassImplicitPairPeer\\Root287::A is deprecated' || $message === 'Constant Ns287ParentedClassImplicitPairPeer\\Root287::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member287peer'] = 'A';
    return true;
}
$set287peer = false;
$get287peer = false;
$outside287peer = new Leaf287();
$member287peer = 'A';
\set_error_handler('Ns287ParentedClassImplicitPairPeer\\notice287');
echo 'B|', selector287()::{member287()}, '|Z|';
unset($outside287peer);
echo 'E|';
\restore_error_handler();
