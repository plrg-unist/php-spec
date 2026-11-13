<?php
namespace Ns262NonpublicVector;
class LeafBase262 {}
class Leaf262 extends LeafBase262 {
    public function __destruct() {
        echo 'L|';
        $GLOBALS['released262vector'] = true;
    }
}
class Middle262 {
    public function __destruct() {
        echo 'P|', $GLOBALS['released262vector'] === false ? 'Q|' : 'BAD|';
    }
}
class Fields262 {
    private LeafBase262 $same;
    protected int $tag;
    protected Middle262 $middle;
    public function __construct(LeafBase262 $leaf262) {
        $this->middle = new Middle262();
        $this->tag = 17;
        $this->same = $leaf262;
    }
    protected function check262($leaf262) {
        echo $this->same === $leaf262 ? 'S|' : 'BAD|';
    }
}
class Wide262 extends Fields262 {
    private $same;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        $leaf262 = new Leaf262();
        $this->same = $leaf262;
        parent::__construct($leaf262);
    }
    public function __destruct() {
        echo 'D|', $this->tag === 17 ? 'I|' : 'BAD|';
        $this->check262($this->same);
        $GLOBALS['member262vector'] = 'B';
    }
}
function &selector262() {
    $receiver262 = new Wide262();
    echo 'W|';
    return $receiver262;
}
function member262() {
    echo 'M|';
    return $GLOBALS['member262vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns262NonpublicVector\\Wide262::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member262vector'] = 'A';
    return true;
});
$released262vector = false;
$member262vector = 'A';
echo 'B|', selector262()::{member262()}, '|Z|';
\restore_error_handler();
