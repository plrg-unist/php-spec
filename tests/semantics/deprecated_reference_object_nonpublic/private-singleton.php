<?php
namespace Ns262NonpublicSingle;
class Leaf262 {
    public function __destruct() {
        echo 'L|';
    }
}
class Selected262 {
    private $edge;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        $this->edge = new Leaf262();
    }
    public function __destruct() {
        echo 'D|', $this->edge === null ? 'BAD|' : 'I|';
        $GLOBALS['member262single'] = 'B';
    }
}
function &selector262() {
    $receiver262 = new Selected262();
    echo 'C|';
    return $receiver262;
}
function member262() {
    echo 'M|';
    return $GLOBALS['member262single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns262NonpublicSingle\\Selected262::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member262single'] = 'A';
    return true;
});
$member262single = 'A';
echo 'B|', selector262()::{member262()}, '|Z|';
\restore_error_handler();
