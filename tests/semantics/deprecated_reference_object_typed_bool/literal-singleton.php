<?php
namespace Ns251Bool;
class Selected251 {
    public bool $tag;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === false ? 'T|' : 'BAD|';
        $GLOBALS['member251bool'] = 'B';
    }
}
function &selector251() {
    $receiver251 = new Selected251();
    $receiver251->tag = false;
    echo 'C|';
    return $receiver251;
}
function member251() {
    echo 'M|';
    return $GLOBALS['member251bool'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns251Bool\\Selected251::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member251bool'] = 'A';
    return true;
});
$member251bool = 'A';
echo 'B|', selector251()::{member251()}, '|Z|';
\restore_error_handler();
