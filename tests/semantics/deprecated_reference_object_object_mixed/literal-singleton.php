<?php
namespace Ns259ObjectMixedSingle;
class LeafBase259 {}
class Leaf259 extends LeafBase259 {
    public function __destruct() {
        echo 'L|';
    }
}
class Selected259 {
    public mixed $edge;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|';
        $GLOBALS['member259single'] = 'B';
    }
}
function &selector259() {
    $receiver259 = new Selected259();
    $receiver259->edge = new Leaf259();
    echo 'C|';
    return $receiver259;
}
function member259() {
    echo 'M|';
    return $GLOBALS['member259single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns259ObjectMixedSingle\\Selected259::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member259single'] = 'A';
    return true;
});
$member259single = 'A';
echo 'B|', selector259()::{member259()}, '|Z|';
\restore_error_handler();
