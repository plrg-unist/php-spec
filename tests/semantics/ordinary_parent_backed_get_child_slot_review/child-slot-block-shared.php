<?php
namespace Ns290BackedChildSlotBlockPeer;
class Leaf290 {
    public function __destruct() { echo 'L|'; }
}
class PadLeaf290 {
    public function __destruct() { echo 'U|'; }
}
class Middle290 {
    public $pad = true;
    public $edge;
    public function __construct() { $this->edge = $GLOBALS['outside290peer']; }
    public function __destruct() { echo 'I|', $this->pad === true ? 'F|' : 'BAD|'; }
}
class Tail290 {
    public $edge;
    public function __construct() { $this->edge = $GLOBALS['outside290peer']; }
    public function __destruct() { echo 'T|'; }
}
class Parent290 {
    public $anchor = 31;
    public $pad = 99;
}
class Root290 extends Parent290 {
    public $middle;
    public $pad {
        get {
            $backing = $this->pad;
            $GLOBALS['get290peer'] = $backing === null;
            return 7;
        }
    }
    public $tail;
    public function __construct() {
        $raw = (array)$this;
        echo $raw['anchor'] === 31 && $raw['pad'] === null && $GLOBALS['get290peer'] === false ? 'Q|' : 'BAD|';
        echo $this->pad === 7 && $GLOBALS['get290peer'] === true ? 'G|' : 'BAD|';
        $GLOBALS['get290peer'] = false;
        $this->middle = new Middle290();
        $this->pad = new PadLeaf290();
        $this->tail = new Tail290();
        echo $GLOBALS['get290peer'] === false ? 'W|' : 'BAD|';
    }
    public function __destruct() {
        echo $this->anchor === 31 && $GLOBALS['get290peer'] === false ? 'R|' : 'BAD|';
    }
}
$get290peer = false;
$outside290peer = new Leaf290();
echo 'B|';
$root290 = new Root290();
echo 'C|';
unset($root290);
echo 'Z|';
unset($outside290peer);
echo 'E|';
