<?php
namespace Ns258ClassUnionSingle;
class LeafBase258 {}
class Leaf258 extends LeafBase258 {
    public function __destruct() {
        echo 'L|';
    }
}
class Selected258 {
    public ?LeafBase258 $edge;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|';
        $GLOBALS['member258single'] = 'B';
    }
}
function &selector258() {
    $receiver258 = new Selected258();
    $receiver258->edge = new Leaf258();
    echo 'C|';
    return $receiver258;
}
function member258() {
    echo 'M|';
    return $GLOBALS['member258single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns258ClassUnionSingle\\Selected258::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member258single'] = 'A';
    return true;
});
$member258single = 'A';
echo 'B|', selector258()::{member258()}, '|Z|';
\restore_error_handler();
