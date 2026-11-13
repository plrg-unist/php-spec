<?php
namespace Ns271UntypedTraitSetExplicitPlainVector;
class LeafBase271 {}
class Leaf271 extends LeafBase271 {
    public function __destruct() {
        echo 'L|';
        $GLOBALS['released271vector'] = true;
    }
}
class Middle271 {
    public function __destruct() {
        echo 'P|', $GLOBALS['released271vector'] === false ? 'Q|' : 'BAD|';
    }
}
trait Tag271 {
    public $tag = false {
        set($received271) {
            $GLOBALS['called271vector'] = true;
            $this->tag = $received271;
        }
    }
}
class Fields271 {
    use Tag271;
    public $first;
    public $middle;
    public $last;
    public function __construct() {
        $leaf271 = new Leaf271();
        $this->last = $leaf271;
        $this->middle = new Middle271();
        $this->first = $leaf271;
    }
}
class Wide271 extends Fields271 {
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === false ? 'I|' : 'BAD|';
        $GLOBALS['member271vector'] = 'B';
    }
}
function &selector271() {
    $receiver271 = new Wide271();
    echo 'W|';
    return $receiver271;
}
function member271() {
    echo 'M|';
    return $GLOBALS['member271vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns271UntypedTraitSetExplicitPlainVector\\Wide271::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member271vector'] = 'A';
    return true;
});
$called271vector = false;
$released271vector = false;
$member271vector = 'A';
echo 'B|', selector271()::{member271()}, '|', $called271vector === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
