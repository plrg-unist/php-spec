<?php
namespace Ns275UntypedPairSingle;
class Selected275 {
    public $tag = 17 {
        set { $GLOBALS['set275single'] = true; $this->tag = $value; }
        get { $GLOBALS['get275single'] = true; return $this->tag; }
    }
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === 17 ? 'I|' : 'BAD|';
        $GLOBALS['member275single'] = 'B';
    }
}
function &selector275() {
    $receiver275 = new Selected275();
    echo 'C|';
    return $receiver275;
}
function member275() {
    echo 'M|';
    return $GLOBALS['member275single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns275UntypedPairSingle\\Selected275::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member275single'] = 'A';
    return true;
});
$get275single = false;
$set275single = false;
$member275single = 'A';
echo 'B|', selector275()::{member275()}, '|', $get275single === true && $set275single === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
