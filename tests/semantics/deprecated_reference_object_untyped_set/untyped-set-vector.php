<?php
namespace Ns267UntypedSetVector;
class LeafBase267 {}
class Leaf267 extends LeafBase267 {
    public function __destruct() {
        echo 'L|';
        $GLOBALS['released267vector'] = true;
    }
}
class Middle267 {
    public function __destruct() {
        echo 'P|', $GLOBALS['released267vector'] === false ? 'Q|' : 'BAD|';
    }
}
class Fields267 {
    public $first {
        get {
            $GLOBALS['called267vector'] = true;
            return $this->first;
        }
    }
    public $tag = false {
        set {
            $GLOBALS['called267vector'] = true;
            $this->tag = $value;
        }
    }
    public $middle;
    public $last {
        get {
            $GLOBALS['called267vector'] = true;
            return $this->last;
        }
    }
    public function __construct() {
        $leaf267 = new Leaf267();
        $this->last = $leaf267;
        $this->middle = new Middle267();
        $this->first = $leaf267;
    }
}
class Wide267 extends Fields267 {
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === false ? 'I|' : 'BAD|';
        $GLOBALS['member267vector'] = 'B';
    }
}
function &selector267() {
    $receiver267 = new Wide267();
    echo 'W|';
    return $receiver267;
}
function member267() {
    echo 'M|';
    return $GLOBALS['member267vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns267UntypedSetVector\\Wide267::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member267vector'] = 'A';
    return true;
});
$called267vector = false;
$released267vector = false;
$member267vector = 'A';
echo 'B|', selector267()::{member267()}, '|', $called267vector === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
