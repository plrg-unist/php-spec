<?php
namespace Ns257TypedClassSingle;
class LeafBase257 {}
class Leaf257 extends LeafBase257 {
    public function __destruct() {
        echo 'L|';
    }
}
class Selected257 {
    public LeafBase257 $edge;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|';
        $GLOBALS['member257single'] = 'B';
    }
}
function &selector257() {
    $receiver257 = new Selected257();
    $receiver257->edge = new Leaf257();
    echo 'C|';
    return $receiver257;
}
function member257() {
    echo 'M|';
    return $GLOBALS['member257single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns257TypedClassSingle\\Selected257::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member257single'] = 'A';
    return true;
});
$member257single = 'A';
echo 'B|', selector257()::{member257()}, '|Z|';
\restore_error_handler();
