<?php
namespace Ns247Literal;
class Selected247 {
    public $tag;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === 'tag' ? 'S|' : 'BAD|';
        $GLOBALS['member247literal'] = 'B';
    }
}
function &selector247() {
    $receiver247 = new Selected247();
    $receiver247->tag = 'tag';
    echo 'C|';
    return $receiver247;
}
function member247() {
    echo 'M|';
    return $GLOBALS['member247literal'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns247Literal\\Selected247::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member247literal'] = 'A';
    return true;
});
$member247literal = 'A';
echo 'B|', selector247()::{member247()}, '|Z|';
\restore_error_handler();
