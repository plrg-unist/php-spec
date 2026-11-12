<?php
namespace Ns249Float;
class Selected249 {
    public float $tag;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === 1.5 ? 'F|' : 'BAD|';
        $GLOBALS['member249float'] = 'B';
    }
}
function &selector249() {
    $receiver249 = new Selected249();
    $receiver249->tag = 1.5;
    echo 'C|';
    return $receiver249;
}
function member249() {
    echo 'M|';
    return $GLOBALS['member249float'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns249Float\\Selected249::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member249float'] = 'A';
    return true;
});
$member249float = 'A';
echo 'B|', selector249()::{member249()}, '|Z|';
\restore_error_handler();
