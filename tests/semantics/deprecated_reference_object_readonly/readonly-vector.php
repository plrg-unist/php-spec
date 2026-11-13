<?php
namespace Ns261ReadonlyVector;
class LeafBase261 {}
class Leaf261 extends LeafBase261 {
    public function __destruct() {
        echo 'L|';
        $GLOBALS['released261vector'] = true;
    }
}
class Middle261 {
    public function __destruct() {
        echo 'P|', $GLOBALS['released261vector'] === false ? 'Q|' : 'BAD|';
    }
}
class Fields261 {
    public readonly LeafBase261 $first;
    public readonly int $tag;
    public readonly Middle261 $middle;
    public readonly LeafBase261 $last;
    public function __construct() {
        $leaf261 = new Leaf261();
        $this->last = $leaf261;
        $this->first = $leaf261;
        $this->middle = new Middle261();
        $this->tag = 17;
    }
}
class Wide261 extends Fields261 {
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === 17 ? 'I|' : 'BAD|';
        $GLOBALS['member261vector'] = 'B';
    }
}
function &selector261() {
    $receiver261 = new Wide261();
    echo 'W|';
    return $receiver261;
}
function member261() {
    echo 'M|';
    return $GLOBALS['member261vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns261ReadonlyVector\\Wide261::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member261vector'] = 'A';
    return true;
});
$released261vector = false;
$member261vector = 'A';
echo 'B|', selector261()::{member261()}, '|Z|';
\restore_error_handler();
