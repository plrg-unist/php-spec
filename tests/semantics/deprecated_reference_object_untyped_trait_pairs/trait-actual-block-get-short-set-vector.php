<?php
namespace Ns280UntypedPairActualParamVector;
class LeafBase280 {}
class Leaf280 extends LeafBase280 {
    public function __destruct() {
        echo 'L|';
        $GLOBALS['released280vector'] = true;
    }
}
class Middle280 {
    public function __destruct() {
        echo 'P|', $GLOBALS['released280vector'] === false ? 'Q|' : 'BAD|';
    }
}
trait Tags280 {
    public $tag {
        get { $GLOBALS['get280vector'] = true; return $this->tag; }
        set($received280vector) => ($GLOBALS['set280vector'] = true) ? $received280vector : $received280vector;
    }
}
class Fields280 {
    public $first;
    use Tags280;
    public $middle;
    public $last;
    public function __construct() {
        $leaf280 = new Leaf280();
        $this->last = $leaf280;
        $this->middle = new Middle280();
        $this->first = $leaf280;
    }
}
class Wide280 extends Fields280 {
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === null ? 'I|' : 'BAD|';
        $GLOBALS['member280vector'] = 'B';
    }
}
function &selector280() {
    $receiver280 = new Wide280();
    echo 'W|';
    return $receiver280;
}
function member280() {
    echo 'M|';
    return $GLOBALS['member280vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns280UntypedPairActualParamVector\\Wide280::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member280vector'] = 'A';
    return true;
});
$get280vector = false;
$set280vector = false;
$released280vector = false;
$member280vector = 'A';
echo 'B|', selector280()::{member280()}, '|', $get280vector === true && $set280vector === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
