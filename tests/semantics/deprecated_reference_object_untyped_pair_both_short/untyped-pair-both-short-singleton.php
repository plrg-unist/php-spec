<?php
namespace Ns278UntypedPairBothShortSingle;
class Selected278 {
    public $tag = 17 {
        set => ($GLOBALS['set278single'] = true) ? $value : $value;
        get => ($GLOBALS['get278single'] = true) ? $this->tag : $this->tag;
    }
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === 17 ? 'I|' : 'BAD|';
        $GLOBALS['member278single'] = 'B';
    }
}
function &selector278() {
    $receiver278 = new Selected278();
    echo 'C|';
    return $receiver278;
}
function member278() {
    echo 'M|';
    return $GLOBALS['member278single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns278UntypedPairBothShortSingle\\Selected278::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member278single'] = 'A';
    return true;
});
$get278single = false;
$set278single = false;
$member278single = 'A';
echo 'B|', selector278()::{member278()}, '|', $get278single === true && $set278single === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
