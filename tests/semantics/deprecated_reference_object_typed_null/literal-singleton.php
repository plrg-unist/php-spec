<?php
namespace Ns254Null;
class Selected254 {
    public null $tag;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === null ? 'N|' : 'BAD|';
        $GLOBALS['member254null'] = 'B';
    }
}
function &selector254() {
    $receiver254 = new Selected254();
    $receiver254->tag = null;
    echo 'C|';
    return $receiver254;
}
function member254() {
    echo 'M|';
    return $GLOBALS['member254null'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns254Null\\Selected254::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member254null'] = 'A';
    return true;
});
$member254null = 'A';
echo 'B|', selector254()::{member254()}, '|Z|';
\restore_error_handler();
