<?php
namespace Ns274UntypedTraitImplicitShortSetVector;
class LeafBase274 {}
class Leaf274 extends LeafBase274 {
    public function __destruct() {
        echo 'L|';
        $GLOBALS['released274vector'] = true;
    }
}
class Middle274 {
    public function __destruct() {
        echo 'P|', $GLOBALS['released274vector'] === false ? 'Q|' : 'BAD|';
    }
}
trait Tag274 {
    public $tag = false {
        set => ($GLOBALS['called274vector'] = true) ? false : $value;
    }
}
class Fields274 {
    use Tag274;
    public $first;
    public $middle;
    public $last;
    public function __construct() {
        $leaf274 = new Leaf274();
        $this->last = $leaf274;
        $this->middle = new Middle274();
        $this->first = $leaf274;
    }
}
class Wide274 extends Fields274 {
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === false ? 'I|' : 'BAD|';
        $GLOBALS['member274vector'] = 'B';
    }
}
function &selector274() {
    $receiver274 = new Wide274();
    echo 'W|';
    return $receiver274;
}
function member274() {
    echo 'M|';
    return $GLOBALS['member274vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns274UntypedTraitImplicitShortSetVector\\Wide274::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member274vector'] = 'A';
    return true;
});
$called274vector = false;
$released274vector = false;
$member274vector = 'A';
echo 'B|', selector274()::{member274()}, '|', $called274vector === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
