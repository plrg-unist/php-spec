<?php
namespace Ns263ModifiersVector;
class LeafBase263 {}
class Leaf263 extends LeafBase263 {
    public function __destruct() {
        echo 'L|';
        $GLOBALS['released263vector'] = true;
    }
}
class Middle263 {
    public function __destruct() {
        echo 'P|', $GLOBALS['released263vector'] === false ? 'Q|' : 'BAD|';
    }
}
class Fields263 {
    public protected(set) LeafBase263 $first;
    public private(set) int $tag;
    protected private(set) Middle263 $middle;
    private readonly LeafBase263 $last;
    public function __construct() {
        $leaf263 = new Leaf263();
        $this->last = $leaf263;
        $this->middle = new Middle263();
        $this->tag = 17;
        $this->first = $leaf263;
    }
    protected function check263() {
        echo $this->last === $this->first ? 'S|' : 'BAD|';
    }
}
class Wide263 extends Fields263 {
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === 17 ? 'I|' : 'BAD|';
        $this->check263();
        $GLOBALS['member263vector'] = 'B';
    }
}
function &selector263() {
    $receiver263 = new Wide263();
    echo 'W|';
    return $receiver263;
}
function member263() {
    echo 'M|';
    return $GLOBALS['member263vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns263ModifiersVector\\Wide263::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member263vector'] = 'A';
    return true;
});
$released263vector = false;
$member263vector = 'A';
echo 'B|', selector263()::{member263()}, '|Z|';
\restore_error_handler();
