<?php
namespace Ns279UntypedPairActualParamVector;
class LeafBase279 {}
class Leaf279 extends LeafBase279 {
    public function __destruct() {
        echo 'L|';
        $GLOBALS['released279vector'] = true;
    }
}
class Middle279 {
    public function __destruct() {
        echo 'P|', $GLOBALS['released279vector'] === false ? 'Q|' : 'BAD|';
    }
}
class Fields279 {
    public $first;
    public $tag {
        get { $GLOBALS['get279vector'] = true; return $this->tag; }
        set($received279vector) => ($GLOBALS['set279vector'] = true) ? $received279vector : $received279vector;
    }
    public $middle;
    public $last;
    public function __construct() {
        $leaf279 = new Leaf279();
        $this->last = $leaf279;
        $this->middle = new Middle279();
        $this->first = $leaf279;
    }
}
class Wide279 extends Fields279 {
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === null ? 'I|' : 'BAD|';
        $GLOBALS['member279vector'] = 'B';
    }
}
function &selector279() {
    $receiver279 = new Wide279();
    echo 'W|';
    return $receiver279;
}
function member279() {
    echo 'M|';
    return $GLOBALS['member279vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns279UntypedPairActualParamVector\\Wide279::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member279vector'] = 'A';
    return true;
});
$get279vector = false;
$set279vector = false;
$released279vector = false;
$member279vector = 'A';
echo 'B|', selector279()::{member279()}, '|', $get279vector === true && $set279vector === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
