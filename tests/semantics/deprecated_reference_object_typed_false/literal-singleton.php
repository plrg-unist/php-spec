<?php
namespace Ns252False;
class Selected252 {
    public false $tag;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === false ? 'T|' : 'BAD|';
        $GLOBALS['member252false'] = 'B';
    }
}
function &selector252() {
    $receiver252 = new Selected252();
    $receiver252->tag = false;
    echo 'C|';
    return $receiver252;
}
function member252() {
    echo 'M|';
    return $GLOBALS['member252false'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns252False\\Selected252::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member252false'] = 'A';
    return true;
});
$member252false = 'A';
echo 'B|', selector252()::{member252()}, '|Z|';
\restore_error_handler();
