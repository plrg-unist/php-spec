<?php
namespace Ns261ReadonlySingle;
class LeafBase261 {}
class Leaf261 extends LeafBase261 {
    public function __destruct() {
        echo 'L|';
    }
}
class Selected261 {
    public readonly LeafBase261 $edge;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        $this->edge = new Leaf261();
    }
    public function __destruct() {
        echo 'D|';
        $GLOBALS['member261single'] = 'B';
    }
}
function &selector261() {
    $receiver261 = new Selected261();
    echo 'C|';
    return $receiver261;
}
function member261() {
    echo 'M|';
    return $GLOBALS['member261single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns261ReadonlySingle\\Selected261::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member261single'] = 'A';
    return true;
});
$member261single = 'A';
echo 'B|', selector261()::{member261()}, '|Z|';
\restore_error_handler();
