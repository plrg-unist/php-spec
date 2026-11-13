<?php
namespace Ns277UntypedPairShortSetVector;
class LeafBase277 {}
class Leaf277 extends LeafBase277 {
    public function __destruct() {
        echo 'L|';
        $GLOBALS['released277vector'] = true;
    }
}
class Middle277 {
    public function __destruct() {
        echo 'P|', $GLOBALS['released277vector'] === false ? 'Q|' : 'BAD|';
    }
}
class Fields277 {
    public $first;
    public $tag {
        get { $GLOBALS['get277vector'] = true; return $this->tag; }
        set => ($GLOBALS['set277vector'] = true) ? $value : $value;
    }
    public $middle;
    public $last;
    public function __construct() {
        $leaf277 = new Leaf277();
        $this->last = $leaf277;
        $this->middle = new Middle277();
        $this->first = $leaf277;
    }
}
class Wide277 extends Fields277 {
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === null ? 'I|' : 'BAD|';
        $GLOBALS['member277vector'] = 'B';
    }
}
function &selector277() {
    $receiver277 = new Wide277();
    echo 'W|';
    return $receiver277;
}
function member277() {
    echo 'M|';
    return $GLOBALS['member277vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns277UntypedPairShortSetVector\\Wide277::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member277vector'] = 'A';
    return true;
});
$get277vector = false;
$set277vector = false;
$released277vector = false;
$member277vector = 'A';
echo 'B|', selector277()::{member277()}, '|', $get277vector === true && $set277vector === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
