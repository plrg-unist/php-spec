<?php
namespace Ns253Vector;
class Base253 {
    public true $tag;
    public function __destruct() {
        echo 'D|', $this->tag === true ? 'T|' : 'BAD|';
        $GLOBALS['member253vector'] = 'B';
    }
}
class Wide253 extends Base253 {
    public $pad;
    #[\Deprecated]
    public const A = 9, B = 10;
}
function &wide253() {
    $receiver253 = new Wide253();
    $receiver253->pad = 17;
    $receiver253->tag = true;
    echo 'W|';
    return $receiver253;
}
function member253() {
    echo 'M|';
    return $GLOBALS['member253vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns253Vector\\Wide253::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member253vector'] = 'A';
    return true;
});
$member253vector = 'A';
echo 'B|', wide253()::{member253()}, '|Z|';
\restore_error_handler();
