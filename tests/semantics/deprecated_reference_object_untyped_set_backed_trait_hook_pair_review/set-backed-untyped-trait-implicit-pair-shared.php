<?php
namespace Ns283SetBackedTraitImplicitPairPeer;
class Leaf283 {
    public function __destruct() {
        echo 'L|';
    }
}
class Middle283 {
    public $pad = true;
    public $edge;
    public function __construct() {
        $this->edge = $GLOBALS['outside283peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === true ? 'F|' : 'BAD|';
    }
}
trait RootPad283 {
    public $pad {
        set {
            $GLOBALS['set283peer'] = true;
            $this->pad = $value;
        }
        get => ($GLOBALS['get283peer'] = true) ? 7 : 7;
    }
}
class Parent283 {
    public $anchor = 31;
}
class Root283 extends Parent283 {
    use RootPad283;
    public $middle;
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        echo $this->anchor === 31 && $this->pad === 7 && $GLOBALS['get283peer'] === true && $GLOBALS['set283peer'] === false ? 'Q|' : 'BAD|';
        $GLOBALS['get283peer'] = false;
        $this->middle = new Middle283();
        $this->tail = $GLOBALS['outside283peer'];
    }
    public function __destruct() {
        echo $this->anchor === 31 ? 'R|' : 'BAD|';
        echo 'D|', Root283::A, '|', 'P|';
        $GLOBALS['member283peer'] = 'B';
    }
}
function &selector283() {
    $receiver283 = new Root283();
    echo 'C|';
    return $receiver283;
}
function member283() {
    echo 'M|', ($GLOBALS['set283peer'] === false && $GLOBALS['get283peer'] === false) ? 'N|' : 'BAD|';
    return $GLOBALS['member283peer'];
}
function notice283($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns283SetBackedTraitImplicitPairPeer\\Root283::A is deprecated' || $message === 'Constant Ns283SetBackedTraitImplicitPairPeer\\Root283::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member283peer'] = 'A';
    return true;
}
$set283peer = false;
$get283peer = false;
$outside283peer = new Leaf283();
$member283peer = 'A';
\set_error_handler('Ns283SetBackedTraitImplicitPairPeer\\notice283');
echo 'B|', selector283()::{member283()}, '|Z|';
unset($outside283peer);
echo 'E|';
\restore_error_handler();
