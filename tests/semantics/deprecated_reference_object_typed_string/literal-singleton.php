<?php
namespace Ns248Literal;
class Selected248 {
    public string $tag;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === 'tag' ? 'S|' : 'BAD|';
        $GLOBALS['member248literal'] = 'B';
    }
}
function &selector248() {
    $receiver248 = new Selected248();
    $receiver248->tag = 'tag';
    echo 'C|';
    return $receiver248;
}
function member248() {
    echo 'M|';
    return $GLOBALS['member248literal'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns248Literal\\Selected248::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member248literal'] = 'A';
    return true;
});
$member248literal = 'A';
echo 'B|', selector248()::{member248()}, '|Z|';
\restore_error_handler();
