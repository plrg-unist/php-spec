<?php
namespace Ns292ShortReferenceNullPeer;
class Leaf292 {
    public function __destruct() { echo 'L|'; }
}
class PadLeaf292 {
    public function __destruct() { echo 'U|'; }
}
class Middle292 {
    public $pad = true;
    public $edge;
    public function __construct() { $this->edge = $GLOBALS['outside292peer']; }
    public function __destruct() { echo 'I|', $this->pad === true ? 'F|' : 'BAD|'; }
}
class Tail292 {
    public $edge;
    public function __construct() { $this->edge = $GLOBALS['outside292peer']; }
    public function __destruct() { echo 'T|'; }
}
class Root292 {
    public $middle;
    public $pad {
        &get =>
            $this->pad;
    }
    public $tail;
    public function __construct() {
        $raw = (array)$this;
        echo $raw['pad'] === null ? 'Q|' : 'BAD|';
    }
    public function __destruct() { echo 'R|'; }
}
$outside292peer = new Leaf292();
echo 'B|';
$root292 = new Root292();
$alias292peer =& $root292->pad;
echo $alias292peer === null ? 'G|' : 'BAD|';
$root292->middle = new Middle292();
$alias292peer = new PadLeaf292();
echo $alias292peer instanceof PadLeaf292 ? 'W|' : 'BAD|';
unset($alias292peer);
$root292->tail = new Tail292();
echo 'C|';
unset($root292);
echo 'Z|';
unset($outside292peer);
echo 'E|';
