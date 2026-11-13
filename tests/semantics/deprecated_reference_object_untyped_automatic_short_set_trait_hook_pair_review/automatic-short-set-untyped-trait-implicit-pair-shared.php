<?php
namespace Ns284AutomaticShortSetTraitImplicitPairPeer;
class Leaf284 {
    public function __destruct() {
        echo 'L|';
    }
}
class PadLeaf284 {
    public function __destruct() {
        echo 'U|';
    }
}
class Middle284 {
    public $pad = true;
    public $edge;
    public function __construct() {
        $this->edge = $GLOBALS['outside284peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === true ? 'F|' : 'BAD|';
    }
}
trait RootPad284 {
    public $pad {
        set => ($GLOBALS['set284peer'] = true) ? $value : $value;
        get {
            $GLOBALS['get284peer'] = true;
            return 7;
        }
    }
}
class Parent284 {
    public $anchor = 31;
}
class Root284 extends Parent284 {
    use RootPad284;
    public $middle;
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        echo $this->anchor === 31 && $this->pad === 7 && $GLOBALS['get284peer'] === true && $GLOBALS['set284peer'] === false ? 'Q|' : 'BAD|';
        $GLOBALS['get284peer'] = false;
        $this->pad = new PadLeaf284();
        echo $GLOBALS['set284peer'] === true ? 'S|' : 'BAD|';
        $GLOBALS['set284peer'] = false;
        $this->middle = new Middle284();
        $this->tail = $GLOBALS['outside284peer'];
    }
    public function __destruct() {
        echo $this->anchor === 31 ? 'R|' : 'BAD|';
        echo 'D|', Root284::A, '|', 'P|';
        $GLOBALS['member284peer'] = 'B';
    }
}
function &selector284() {
    $receiver284 = new Root284();
    echo 'C|';
    return $receiver284;
}
function member284() {
    echo 'M|', ($GLOBALS['set284peer'] === false && $GLOBALS['get284peer'] === false) ? 'N|' : 'BAD|';
    return $GLOBALS['member284peer'];
}
function notice284($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns284AutomaticShortSetTraitImplicitPairPeer\\Root284::A is deprecated' || $message === 'Constant Ns284AutomaticShortSetTraitImplicitPairPeer\\Root284::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member284peer'] = 'A';
    return true;
}
$set284peer = false;
$get284peer = false;
$outside284peer = new Leaf284();
$member284peer = 'A';
\set_error_handler('Ns284AutomaticShortSetTraitImplicitPairPeer\\notice284');
echo 'B|', selector284()::{member284()}, '|Z|';
unset($outside284peer);
echo 'E|';
\restore_error_handler();
