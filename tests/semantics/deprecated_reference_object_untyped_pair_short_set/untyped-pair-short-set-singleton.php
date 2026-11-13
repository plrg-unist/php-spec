<?php
namespace Ns277UntypedPairShortSetSingle;
class Selected277 {
    public $tag = 17 {
        set => ($GLOBALS['set277single'] = true) ? $value : $value;
        get { $GLOBALS['get277single'] = true; return $this->tag; }
    }
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === 17 ? 'I|' : 'BAD|';
        $GLOBALS['member277single'] = 'B';
    }
}
function &selector277() {
    $receiver277 = new Selected277();
    echo 'C|';
    return $receiver277;
}
function member277() {
    echo 'M|';
    return $GLOBALS['member277single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns277UntypedPairShortSetSingle\\Selected277::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member277single'] = 'A';
    return true;
});
$get277single = false;
$set277single = false;
$member277single = 'A';
echo 'B|', selector277()::{member277()}, '|', $get277single === true && $set277single === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
