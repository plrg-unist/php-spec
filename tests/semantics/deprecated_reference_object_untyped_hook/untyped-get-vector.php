<?php
namespace Ns266UntypedHookVector;
class LeafBase266 {}
class Leaf266 extends LeafBase266 {
    public function __destruct() {
        echo 'L|';
        $GLOBALS['released266vector'] = true;
    }
}
class Middle266 {
    public function __destruct() {
        echo 'P|', $GLOBALS['released266vector'] === false ? 'Q|' : 'BAD|';
    }
}
class Fields266 {
    public $first {
        get {
            $GLOBALS['called266vector'] = true;
            return $this->first;
        }
    }
    public $tag = 17 {
        get {
            $GLOBALS['called266vector'] = true;
            return $this->tag;
        }
    }
    public $middle {
        get {
            $GLOBALS['called266vector'] = true;
            return $this->middle;
        }
    }
    public $last {
        get {
            $GLOBALS['called266vector'] = true;
            return $this->last;
        }
    }
    public function __construct() {
        $leaf266 = new Leaf266();
        $this->last = $leaf266;
        $this->middle = new Middle266();
        $this->first = $leaf266;
    }
}
class Wide266 extends Fields266 {
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|';
        $GLOBALS['member266vector'] = 'B';
    }
}
function &selector266() {
    $receiver266 = new Wide266();
    echo 'W|';
    return $receiver266;
}
function member266() {
    echo 'M|';
    return $GLOBALS['member266vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns266UntypedHookVector\\Wide266::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member266vector'] = 'A';
    return true;
});
$called266vector = false;
$released266vector = false;
$member266vector = 'A';
echo 'B|', selector266()::{member266()}, '|', $called266vector === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
