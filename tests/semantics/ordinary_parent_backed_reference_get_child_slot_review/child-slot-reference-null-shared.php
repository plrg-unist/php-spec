<?php
namespace Ns291ReferenceChildSlotNullPeer;
class Leaf291 {
    public function __destruct() { echo 'L|'; }
}
class PadLeaf291 {
    public function __destruct() { echo 'U|'; }
}
class Middle291 {
    public $pad = true;
    public $edge;
    public function __construct() { $this->edge = $GLOBALS['outside291peer']; }
    public function __destruct() { echo 'I|', $this->pad === true ? 'F|' : 'BAD|'; }
}
class Tail291 {
    public $edge;
    public function __construct() { $this->edge = $GLOBALS['outside291peer']; }
    public function __destruct() { echo 'T|'; }
}
class Parent291 {
    public $anchor = 31;
    public $pad = 99;
}
class Root291 extends Parent291 {
    public $middle;
    public $pad {
        &get {
            $GLOBALS['get291peer'] = $GLOBALS['get291peer'] + 1;
            return $this->pad;
        }
    }
    public $tail;
    public function __construct() {
        $raw = (array)$this;
        echo $raw['anchor'] === 31 && $raw['pad'] === null && $GLOBALS['get291peer'] === 0 ? 'Q|' : 'BAD|';
    }
    public function __destruct() {
        echo $this->anchor === 31 && $GLOBALS['get291peer'] === 1 ? 'R|' : 'BAD|';
    }
}
$get291peer = 0;
$outside291peer = new Leaf291();
echo 'B|';
$root291 = new Root291();
$alias291peer =& $root291->pad;
echo $alias291peer === null && $get291peer === 1 ? 'G|' : 'BAD|';
$root291->middle = new Middle291();
$alias291peer = new PadLeaf291();
echo $alias291peer instanceof PadLeaf291 && $get291peer === 1 ? 'W|' : 'BAD|';
unset($alias291peer);
$root291->tail = new Tail291();
echo 'C|';
unset($root291);
echo 'Z|';
unset($outside291peer);
echo 'E|';
