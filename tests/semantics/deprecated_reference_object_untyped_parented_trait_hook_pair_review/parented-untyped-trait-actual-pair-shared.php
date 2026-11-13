<?php
namespace Ns281ParentedTraitActualPairPeer;
class Leaf281 {
    public function __destruct() {
        echo 'L|';
    }
}
class Middle281 {
    public $pad = true;
    public $edge;
    public function __construct() {
        $this->edge = $GLOBALS['outside281peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === true ? 'F|' : 'BAD|';
    }
}
trait RootPad281 {
    public $pad {
        set($incoming) => ($GLOBALS['set281peer'] = true) ? $incoming : $incoming;
        get => ($GLOBALS['get281peer'] = true) ? $this->pad : $this->pad;
    }
}
class Parent281 {
    public $anchor = 31;
}
class Root281 extends Parent281 {
    use RootPad281;
    public $middle;
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        echo $this->anchor === 31 && $this->pad === null && $GLOBALS['get281peer'] === true && $GLOBALS['set281peer'] === false ? 'Q|' : 'BAD|';
        $GLOBALS['get281peer'] = false;
        $this->middle = new Middle281();
        $this->tail = $GLOBALS['outside281peer'];
    }
    public function __destruct() {
        echo $this->anchor === 31 ? 'R|' : 'BAD|';
        echo 'D|', Root281::A, '|', 'P|';
        $GLOBALS['member281peer'] = 'B';
    }
}
function &selector281() {
    $receiver281 = new Root281();
    echo 'C|';
    return $receiver281;
}
function member281() {
    echo 'M|', ($GLOBALS['set281peer'] === false && $GLOBALS['get281peer'] === false) ? 'N|' : 'BAD|';
    return $GLOBALS['member281peer'];
}
function notice281($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns281ParentedTraitActualPairPeer\\Root281::A is deprecated' || $message === 'Constant Ns281ParentedTraitActualPairPeer\\Root281::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member281peer'] = 'A';
    return true;
}
$set281peer = false;
$get281peer = false;
$outside281peer = new Leaf281();
$member281peer = 'A';
\set_error_handler('Ns281ParentedTraitActualPairPeer\\notice281');
echo 'B|', selector281()::{member281()}, '|Z|';
unset($outside281peer);
echo 'E|';
\restore_error_handler();
