<?php
namespace Ns268UntypedShortSetVector;
class LeafBase268 {}
class Leaf268 extends LeafBase268 {
    public function __destruct() {
        echo 'L|';
        $GLOBALS['released268vector'] = true;
    }
}
class Middle268 {
    public function __destruct() {
        echo 'P|', $GLOBALS['released268vector'] === false ? 'Q|' : 'BAD|';
    }
}
class Fields268 {
    public $first {
        get {
            $GLOBALS['called268vector'] = true;
            return $this->first;
        }
    }
    public $tag = false {
        set => ($GLOBALS['called268vector'] = true) ? false : $value;
    }
    public $middle;
    public $last {
        get {
            $GLOBALS['called268vector'] = true;
            return $this->last;
        }
    }
    public function __construct() {
        $leaf268 = new Leaf268();
        $this->last = $leaf268;
        $this->middle = new Middle268();
        $this->first = $leaf268;
    }
}
class Wide268 extends Fields268 {
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === false ? 'I|' : 'BAD|';
        $GLOBALS['member268vector'] = 'B';
    }
}
function &selector268() {
    $receiver268 = new Wide268();
    echo 'W|';
    return $receiver268;
}
function member268() {
    echo 'M|';
    return $GLOBALS['member268vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns268UntypedShortSetVector\\Wide268::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member268vector'] = 'A';
    return true;
});
$called268vector = false;
$released268vector = false;
$member268vector = 'A';
echo 'B|', selector268()::{member268()}, '|', $called268vector === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
