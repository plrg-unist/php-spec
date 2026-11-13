<?php
namespace Ns276UntypedPairImplicitDefaultVector;
class LeafBase276 {}
class Leaf276 extends LeafBase276 {
    public function __destruct() {
        echo 'L|';
        $GLOBALS['released276vector'] = true;
    }
}
class Middle276 {
    public function __destruct() {
        echo 'P|', $GLOBALS['released276vector'] === false ? 'Q|' : 'BAD|';
    }
}
class Fields276 {
    public $first;
    public $tag {
        get { $GLOBALS['get276vector'] = true; return $this->tag; }
        set { $GLOBALS['set276vector'] = true; $this->tag = $value; }
    }
    public $middle;
    public $last;
    public function __construct() {
        $leaf276 = new Leaf276();
        $this->last = $leaf276;
        $this->middle = new Middle276();
        $this->first = $leaf276;
    }
}
class Wide276 extends Fields276 {
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === null ? 'I|' : 'BAD|';
        $GLOBALS['member276vector'] = 'B';
    }
}
function &selector276() {
    $receiver276 = new Wide276();
    echo 'W|';
    return $receiver276;
}
function member276() {
    echo 'M|';
    return $GLOBALS['member276vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns276UntypedPairImplicitDefaultVector\\Wide276::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member276vector'] = 'A';
    return true;
});
$get276vector = false;
$set276vector = false;
$released276vector = false;
$member276vector = 'A';
echo 'B|', selector276()::{member276()}, '|', $get276vector === true && $set276vector === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
