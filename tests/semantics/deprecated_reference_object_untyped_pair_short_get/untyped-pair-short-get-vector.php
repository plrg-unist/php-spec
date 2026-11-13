<?php
namespace Ns278UntypedPairShortGetVector;
class LeafBase278 {}
class Leaf278 extends LeafBase278 {
    public function __destruct() {
        echo 'L|';
        $GLOBALS['released278vector'] = true;
    }
}
class Middle278 {
    public function __destruct() {
        echo 'P|', $GLOBALS['released278vector'] === false ? 'Q|' : 'BAD|';
    }
}
class Fields278 {
    public $first;
    public $tag {
        get => ($GLOBALS['get278vector'] = true) ? $this->tag : $this->tag;
        set { $GLOBALS['set278vector'] = true; $this->tag = $value; }
    }
    public $middle;
    public $last;
    public function __construct() {
        $leaf278 = new Leaf278();
        $this->last = $leaf278;
        $this->middle = new Middle278();
        $this->first = $leaf278;
    }
}
class Wide278 extends Fields278 {
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === null ? 'I|' : 'BAD|';
        $GLOBALS['member278vector'] = 'B';
    }
}
function &selector278() {
    $receiver278 = new Wide278();
    echo 'W|';
    return $receiver278;
}
function member278() {
    echo 'M|';
    return $GLOBALS['member278vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns278UntypedPairShortGetVector\\Wide278::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member278vector'] = 'A';
    return true;
});
$get278vector = false;
$set278vector = false;
$released278vector = false;
$member278vector = 'A';
echo 'B|', selector278()::{member278()}, '|', $get278vector === true && $set278vector === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
