<?php
namespace Ns270UntypedSetExplicitVector;
class LeafBase270 {}
class Leaf270 extends LeafBase270 {
    public function __destruct() {
        echo 'L|';
        $GLOBALS['released270vector'] = true;
    }
}
class Middle270 {
    public function __destruct() {
        echo 'P|', $GLOBALS['released270vector'] === false ? 'Q|' : 'BAD|';
    }
}
class Fields270 {
    public $first {
        get {
            $GLOBALS['called270vector'] = true;
            return $this->first;
        }
    }
    public $tag = false {
        set($received270) {
            $GLOBALS['called270vector'] = true;
            $this->tag = $received270;
        }
    }
    public $middle;
    public $last {
        get {
            $GLOBALS['called270vector'] = true;
            return $this->last;
        }
    }
    public function __construct() {
        $leaf270 = new Leaf270();
        $this->last = $leaf270;
        $this->middle = new Middle270();
        $this->first = $leaf270;
    }
}
class Wide270 extends Fields270 {
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === false ? 'I|' : 'BAD|';
        $GLOBALS['member270vector'] = 'B';
    }
}
function &selector270() {
    $receiver270 = new Wide270();
    echo 'W|';
    return $receiver270;
}
function member270() {
    echo 'M|';
    return $GLOBALS['member270vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns270UntypedSetExplicitVector\\Wide270::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member270vector'] = 'A';
    return true;
});
$called270vector = false;
$released270vector = false;
$member270vector = 'A';
echo 'B|', selector270()::{member270()}, '|', $called270vector === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
