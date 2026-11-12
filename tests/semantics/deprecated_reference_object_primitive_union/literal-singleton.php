<?php
namespace Ns256UnionSingle;
class Selected256 {
    public int|string $tag;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === 'tag256' ? 'S|' : 'BAD|';
        $GLOBALS['member256single'] = 'B';
    }
}
function &selector256() {
    $receiver256 = new Selected256();
    $receiver256->tag = 'tag256';
    echo 'C|';
    return $receiver256;
}
function member256() {
    echo 'M|';
    return $GLOBALS['member256single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns256UnionSingle\\Selected256::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member256single'] = 'A';
    return true;
});
$member256single = 'A';
echo 'B|', selector256()::{member256()}, '|Z|';
\restore_error_handler();
