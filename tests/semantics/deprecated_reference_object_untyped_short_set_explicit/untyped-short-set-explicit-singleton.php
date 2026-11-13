<?php
namespace Ns269UntypedShortSetExplicitSingle;
class Selected269 {
    public $tag = 17 {
        set($incoming269) => ($GLOBALS['called269single'] = true) ? 99 : $incoming269;
    }
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === 17 ? 'I|' : 'BAD|';
        $GLOBALS['member269single'] = 'B';
    }
}
function &selector269() {
    $receiver269 = new Selected269();
    echo 'C|';
    return $receiver269;
}
function member269() {
    echo 'M|';
    return $GLOBALS['member269single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns269UntypedShortSetExplicitSingle\\Selected269::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member269single'] = 'A';
    return true;
});
$called269single = false;
$member269single = 'A';
echo 'B|', selector269()::{member269()}, '|', $called269single === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
