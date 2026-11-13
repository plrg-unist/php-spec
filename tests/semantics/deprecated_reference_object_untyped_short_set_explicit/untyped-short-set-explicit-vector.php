<?php
namespace Ns269UntypedShortSetExplicitVector;
class LeafBase269 {}
class Leaf269 extends LeafBase269 {
    public function __destruct() {
        echo 'L|';
        $GLOBALS['released269vector'] = true;
    }
}
class Middle269 {
    public function __destruct() {
        echo 'P|', $GLOBALS['released269vector'] === false ? 'Q|' : 'BAD|';
    }
}
class Fields269 {
    public $first {
        get {
            $GLOBALS['called269vector'] = true;
            return $this->first;
        }
    }
    public $tag = false {
        set($received269) => ($GLOBALS['called269vector'] = true) ? false : $received269;
    }
    public $middle;
    public $last {
        get {
            $GLOBALS['called269vector'] = true;
            return $this->last;
        }
    }
    public function __construct() {
        $leaf269 = new Leaf269();
        $this->last = $leaf269;
        $this->middle = new Middle269();
        $this->first = $leaf269;
    }
}
class Wide269 extends Fields269 {
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === false ? 'I|' : 'BAD|';
        $GLOBALS['member269vector'] = 'B';
    }
}
function &selector269() {
    $receiver269 = new Wide269();
    echo 'W|';
    return $receiver269;
}
function member269() {
    echo 'M|';
    return $GLOBALS['member269vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns269UntypedShortSetExplicitVector\\Wide269::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member269vector'] = 'A';
    return true;
});
$called269vector = false;
$released269vector = false;
$member269vector = 'A';
echo 'B|', selector269()::{member269()}, '|', $called269vector === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
