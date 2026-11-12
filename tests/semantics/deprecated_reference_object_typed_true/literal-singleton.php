<?php
namespace Ns253True;
class Selected253 {
    public true $tag;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === true ? 'T|' : 'BAD|';
        $GLOBALS['member253true'] = 'B';
    }
}
function &selector253() {
    $receiver253 = new Selected253();
    $receiver253->tag = true;
    echo 'C|';
    return $receiver253;
}
function member253() {
    echo 'M|';
    return $GLOBALS['member253true'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns253True\\Selected253::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member253true'] = 'A';
    return true;
});
$member253true = 'A';
echo 'B|', selector253()::{member253()}, '|Z|';
\restore_error_handler();
