<?php
namespace Ns250Vector;
class Base250 {
    public int $tag;
    public function __destruct() {
        echo 'D|', $this->tag === 17 ? 'T|' : 'BAD|';
        $GLOBALS['member250vector'] = 'B';
    }
}
class Wide250 extends Base250 {
    public $pad;
    #[\Deprecated]
    public const A = 9, B = 10;
}
function &wide250() {
    $receiver250 = new Wide250();
    $receiver250->pad = false;
    $receiver250->tag = 17;
    echo 'W|';
    return $receiver250;
}
function member250() {
    echo 'M|';
    return $GLOBALS['member250vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns250Vector\\Wide250::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member250vector'] = 'A';
    return true;
});
$member250vector = 'A';
echo 'B|', wide250()::{member250()}, '|Z|';
\restore_error_handler();
