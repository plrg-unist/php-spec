<?php
namespace Ns252Vector;
class Base252 {
    public false $tag;
    public function __destruct() {
        echo 'D|', $this->tag === false ? 'T|' : 'BAD|';
        $GLOBALS['member252vector'] = 'B';
    }
}
class Wide252 extends Base252 {
    public $pad;
    #[\Deprecated]
    public const A = 9, B = 10;
}
function &wide252() {
    $receiver252 = new Wide252();
    $receiver252->pad = 17;
    $receiver252->tag = false;
    echo 'W|';
    return $receiver252;
}
function member252() {
    echo 'M|';
    return $GLOBALS['member252vector'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns252Vector\\Wide252::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member252vector'] = 'A';
    return true;
});
$member252vector = 'A';
echo 'B|', wide252()::{member252()}, '|Z|';
\restore_error_handler();
