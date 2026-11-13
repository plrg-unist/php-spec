<?php
namespace Ns263ModifiersSingle;
class LeafBase263 {}
class Leaf263 extends LeafBase263 {
    public function __destruct() {
        echo 'L|';
    }
}
class Selected263 {
    public public(set) readonly LeafBase263 $edge;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        $this->edge = new Leaf263();
    }
    public function __destruct() {
        echo 'D|', $this->edge === null ? 'BAD|' : 'I|';
        $GLOBALS['member263single'] = 'B';
    }
}
function &selector263() {
    $receiver263 = new Selected263();
    echo 'C|';
    return $receiver263;
}
function member263() {
    echo 'M|';
    return $GLOBALS['member263single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns263ModifiersSingle\\Selected263::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member263single'] = 'A';
    return true;
});
$member263single = 'A';
echo 'B|', selector263()::{member263()}, '|Z|';
\restore_error_handler();
