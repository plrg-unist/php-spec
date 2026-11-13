<?php
namespace Ns264HookSingle;
class LeafBase264 {}
class Leaf264 extends LeafBase264 {
    public function __destruct() {
        echo 'L|';
    }
}
class Selected264 {
    public LeafBase264 $edge {
        get {
            echo 'BADGET|';
            return $this->edge;
        }
    }
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        $this->edge = new Leaf264();
    }
    public function __destruct() {
        echo 'D|';
        $GLOBALS['member264single'] = 'B';
    }
}
function &selector264() {
    $receiver264 = new Selected264();
    echo 'C|';
    return $receiver264;
}
function member264() {
    echo 'M|';
    return $GLOBALS['member264single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns264HookSingle\\Selected264::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member264single'] = 'A';
    return true;
});
$member264single = 'A';
echo 'B|', selector264()::{member264()}, '|Z|';
\restore_error_handler();
