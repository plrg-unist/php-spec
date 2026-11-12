<?php
namespace Ns245Scalar;
class Base245 {
    public $tag;
    #[\Deprecated]
    public const A = 7, B = 8;
    public function __destruct() {
        echo 'D|', $this->tag === null ? 'N|' : ($this->tag === false ? 'F|' : 'I|'), Child245::A, '|';
        $GLOBALS['member245'] = 'B';
    }
}
class Child245 extends Base245 {
    #[\Deprecated]
    public const A = 9, B = 10;
}
function &selector245() {
    $receiver245 = new Child245();
    $receiver245->tag = $GLOBALS['tag245'];
    echo 'C|';
    return $receiver245;
}
function member245() {
    echo 'M|';
    return $GLOBALS['member245'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns245Scalar\\Child245::A is deprecated' || $message === 'Constant Ns245Scalar\\Child245::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member245'] = 'A';
    return true;
});
$member245 = 'A';
foreach ([null, false, 17] as $tag245) {
    echo 'B|', selector245()::{member245()}, '|Z|';
}
\restore_error_handler();
