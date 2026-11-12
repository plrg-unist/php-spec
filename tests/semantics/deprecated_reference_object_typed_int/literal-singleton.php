<?php
namespace Ns250Int;
class Selected250 {
    public int $tag;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === 17 ? 'T|' : 'BAD|';
        $GLOBALS['member250int'] = 'B';
    }
}
function &selector250() {
    $receiver250 = new Selected250();
    $receiver250->tag = 17;
    echo 'C|';
    return $receiver250;
}
function member250() {
    echo 'M|';
    return $GLOBALS['member250int'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns250Int\\Selected250::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member250int'] = 'A';
    return true;
});
$member250int = 'A';
echo 'B|', selector250()::{member250()}, '|Z|';
\restore_error_handler();
