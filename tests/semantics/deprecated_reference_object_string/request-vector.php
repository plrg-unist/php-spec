<?php
namespace Ns247Request;
class Base247 {
    public $tag;
    public function __destruct() {
        echo 'D|', $this->tag === 'tag' ? 'S|' : 'BAD|';
        $GLOBALS['member247request'] = 'B';
    }
}
class Selected247 extends Base247 {
    public $pad;
    #[\Deprecated]
    public const A = 9, B = 10;
}
function &selector247() {
    $suffix247 = 'g';
    $receiver247 = new Selected247();
    $receiver247->pad = false;
    $receiver247->tag = 'ta' . $suffix247;
    echo 'C|';
    return $receiver247;
}
function member247() {
    echo 'M|';
    return $GLOBALS['member247request'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns247Request\\Selected247::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member247request'] = 'A';
    return true;
});
$member247request = 'A';
echo 'B|', selector247()::{member247()}, '|Z|';
\restore_error_handler();
