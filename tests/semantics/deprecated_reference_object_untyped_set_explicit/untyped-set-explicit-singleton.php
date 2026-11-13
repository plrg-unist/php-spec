<?php
namespace Ns270UntypedSetExplicitSingle;
class Selected270 {
    public $tag = 17 {
        set($incoming270) {
            $GLOBALS['called270single'] = true;
            $this->tag = $incoming270;
        }
    }
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === 17 ? 'I|' : 'BAD|';
        $GLOBALS['member270single'] = 'B';
    }
}
function &selector270() {
    $receiver270 = new Selected270();
    echo 'C|';
    return $receiver270;
}
function member270() {
    echo 'M|';
    return $GLOBALS['member270single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns270UntypedSetExplicitSingle\\Selected270::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member270single'] = 'A';
    return true;
});
$called270single = false;
$member270single = 'A';
echo 'B|', selector270()::{member270()}, '|', $called270single === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
