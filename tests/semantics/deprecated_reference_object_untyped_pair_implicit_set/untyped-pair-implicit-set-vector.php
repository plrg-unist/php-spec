<?php
namespace Ns275UntypedPairVector;
class LeafBase275 {}
class Leaf275 extends LeafBase275 {
    public function __destruct() {
        echo 'L|';
        $GLOBALS['released275vector'] = true;
    }
}
class Middle275 {
    public function __destruct() {
        echo 'P|', $GLOBALS['released275vector'] === false ? 'Q|' : 'BAD|';
    }
}
class Fields275 {
    public $first;
    public $tag = false {
        get { $GLOBALS['get275vector'] = true; return $this->tag; }
        set { $GLOBALS['set275vector'] = true; $this->tag = $value; }
    }
    public $middle;
    public $last;
    public function __construct() {
        $leaf275 = new Leaf275();
        $this->last = $leaf275;
        $this->middle = new Middle275();
        $this->first = $leaf275;
    }
}
class Wide275 extends Fields275 {
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === false ? 'I|' : 'BAD|';
        $GLOBALS['member275vector'] = 'B';
    }
}
function &selector275() {
    $receiver275 = new Wide275();
    echo 'W|';
    return $receiver275;
}
function member275() {
    echo 'M|';
    return $GLOBALS['member275vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns275UntypedPairVector\\Wide275::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member275vector'] = 'A';
    return true;
});
$get275vector = false;
$set275vector = false;
$released275vector = false;
$member275vector = 'A';
echo 'B|', selector275()::{member275()}, '|', $get275vector === true && $set275vector === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
