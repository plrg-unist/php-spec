<?php
namespace Ns289UnbackedChildSlotBlockPeer;
class Leaf289 {
    public function __destruct() { echo 'L|'; }
}
class PadLeaf289 {
    public function __destruct() { echo 'U|'; }
}
class Middle289 {
    public $pad = true;
    public $edge;
    public function __construct() { $this->edge = $GLOBALS['outside289peer']; }
    public function __destruct() { echo 'I|', $this->pad === true ? 'F|' : 'BAD|'; }
}
class Tail289 {
    public $edge;
    public function __construct() { $this->edge = $GLOBALS['outside289peer']; }
    public function __destruct() { echo 'T|'; }
}
class Parent289 {
    public $anchor = 31;
    public $pad = 99;
}
class Root289 extends Parent289 {
    public $middle;
    public $pad {
        get {
            $GLOBALS['get289peer'] = true;
            return 7;
        }
    }
    public $tail;
    public function __construct() {
        $raw = (array)$this;
        echo $raw['anchor'] === 31 && $raw['pad'] === null && $GLOBALS['get289peer'] === false ? 'Q|' : 'BAD|';
        echo $this->pad === 7 && $GLOBALS['get289peer'] === true ? 'G|' : 'BAD|';
        $GLOBALS['get289peer'] = false;
        $this->middle = new Middle289();
        $this->pad = new PadLeaf289();
        $this->tail = new Tail289();
        echo $GLOBALS['get289peer'] === false ? 'W|' : 'BAD|';
    }
    public function __destruct() {
        echo $this->anchor === 31 && $GLOBALS['get289peer'] === false ? 'R|' : 'BAD|';
    }
}
$get289peer = false;
$outside289peer = new Leaf289();
echo 'B|';
$root289 = new Root289();
echo 'C|';
unset($root289);
echo 'Z|';
unset($outside289peer);
echo 'E|';
