<?php
namespace Ns254Vector;
class Base254 {
    public null $tag;
    public function __destruct() {
        echo 'D|', $this->tag === null ? 'N|' : 'BAD|';
        $GLOBALS['member254vector'] = 'B';
    }
}
class Wide254 extends Base254 {
    public $pad;
    #[\Deprecated]
    public const A = 9, B = 10;
}
function &wide254() {
    $receiver254 = new Wide254();
    $receiver254->pad = 17;
    $receiver254->tag = null;
    echo 'W|';
    return $receiver254;
}
function member254() {
    echo 'M|';
    return $GLOBALS['member254vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns254Vector\\Wide254::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member254vector'] = 'A';
    return true;
});
$member254vector = 'A';
echo 'B|', wide254()::{member254()}, '|Z|';
\restore_error_handler();
