<?php
namespace Ns272UntypedTraitShortSetExplicitVector;
class LeafBase272 {}
class Leaf272 extends LeafBase272 {
    public function __destruct() {
        echo 'L|';
        $GLOBALS['released272vector'] = true;
    }
}
class Middle272 {
    public function __destruct() {
        echo 'P|', $GLOBALS['released272vector'] === false ? 'Q|' : 'BAD|';
    }
}
trait Tag272 {
    public $tag = false {
        set($received272) => ($GLOBALS['called272vector'] = true) ? false : $received272;
    }
}
class Fields272 {
    use Tag272;
    public $first;
    public $middle;
    public $last;
    public function __construct() {
        $leaf272 = new Leaf272();
        $this->last = $leaf272;
        $this->middle = new Middle272();
        $this->first = $leaf272;
    }
}
class Wide272 extends Fields272 {
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === false ? 'I|' : 'BAD|';
        $GLOBALS['member272vector'] = 'B';
    }
}
function &selector272() {
    $receiver272 = new Wide272();
    echo 'W|';
    return $receiver272;
}
function member272() {
    echo 'M|';
    return $GLOBALS['member272vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns272UntypedTraitShortSetExplicitVector\\Wide272::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member272vector'] = 'A';
    return true;
});
$called272vector = false;
$released272vector = false;
$member272vector = 'A';
echo 'B|', selector272()::{member272()}, '|', $called272vector === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
