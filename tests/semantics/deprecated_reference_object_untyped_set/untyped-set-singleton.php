<?php
namespace Ns267UntypedSetSingle;
class Selected267 {
    public $tag = 17 {
        set {
            $GLOBALS['called267single'] = true;
            $this->tag = $value;
        }
    }
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === 17 ? 'I|' : 'BAD|';
        $GLOBALS['member267single'] = 'B';
    }
}
function &selector267() {
    $receiver267 = new Selected267();
    echo 'C|';
    return $receiver267;
}
function member267() {
    echo 'M|';
    return $GLOBALS['member267single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns267UntypedSetSingle\\Selected267::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member267single'] = 'A';
    return true;
});
$called267single = false;
$member267single = 'A';
echo 'B|', selector267()::{member267()}, '|', $called267single === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
