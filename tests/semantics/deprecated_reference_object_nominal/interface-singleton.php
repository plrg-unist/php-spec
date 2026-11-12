<?php
namespace Ns260NominalSingle;
interface RootI260 {}
interface ChildI260 extends RootI260 {}
class LeafBase260 implements ChildI260 {}
class Leaf260 extends LeafBase260 {
    public function __destruct() {
        echo 'L|';
    }
}
class Selected260 {
    public RootI260 $edge;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|';
        $GLOBALS['member260single'] = 'B';
    }
}
function &selector260() {
    $receiver260 = new Selected260();
    $receiver260->edge = new Leaf260();
    echo 'C|';
    return $receiver260;
}
function member260() {
    echo 'M|';
    return $GLOBALS['member260single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns260NominalSingle\\Selected260::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member260single'] = 'A';
    return true;
});
$member260single = 'A';
echo 'B|', selector260()::{member260()}, '|Z|';
\restore_error_handler();
