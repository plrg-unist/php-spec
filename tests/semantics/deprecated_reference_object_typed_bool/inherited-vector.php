<?php
namespace Ns251Vector;
class Base251 {
    public bool $tag;
    public function __destruct() {
        echo 'D|', $this->tag === false ? 'T|' : 'BAD|';
        $GLOBALS['member251vector'] = 'B';
    }
}
class Wide251 extends Base251 {
    public $pad;
    #[\Deprecated]
    public const A = 9, B = 10;
}
function &wide251() {
    $receiver251 = new Wide251();
    $receiver251->pad = 17;
    $receiver251->tag = false;
    echo 'W|';
    return $receiver251;
}
function member251() {
    echo 'M|';
    return $GLOBALS['member251vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns251Vector\\Wide251::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member251vector'] = 'A';
    return true;
});
$member251vector = 'A';
echo 'B|', wide251()::{member251()}, '|Z|';
\restore_error_handler();
