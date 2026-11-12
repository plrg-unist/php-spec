<?php
namespace Ns257TypedClassVector;
class LeafBase257 {}
class Leaf257 extends LeafBase257 {
    public function __destruct() {
        echo 'L|';
        $GLOBALS['released257vector'] = true;
    }
}
class Middle257 {
    public function __destruct() {
        echo 'P|', $GLOBALS['released257vector'] === false ? 'Q|' : 'BAD|';
    }
}
class Fields257 {
    public LeafBase257 $first;
    public Middle257 $middle;
    public LeafBase257 $last;
}
class Wide257 extends Fields257 {
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|';
        $GLOBALS['member257vector'] = 'B';
    }
}
function &selector257() {
    $leaf257 = new Leaf257();
    $receiver257 = new Wide257();
    $receiver257->last = $leaf257;
    $receiver257->first = $leaf257;
    $receiver257->middle = new Middle257();
    echo 'W|';
    return $receiver257;
}
function member257() {
    echo 'M|';
    return $GLOBALS['member257vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns257TypedClassVector\\Wide257::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member257vector'] = 'A';
    return true;
});
$released257vector = false;
$member257vector = 'A';
echo 'B|', selector257()::{member257()}, '|Z|';
\restore_error_handler();
