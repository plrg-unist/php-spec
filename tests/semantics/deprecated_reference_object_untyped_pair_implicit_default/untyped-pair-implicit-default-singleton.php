<?php
namespace Ns276UntypedPairImplicitDefaultSingle;
class Selected276 {
    public $tag {
        set { $GLOBALS['set276single'] = true; $this->tag = $value; }
        get { $GLOBALS['get276single'] = true; return $this->tag; }
    }
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === null ? 'I|' : 'BAD|';
        $GLOBALS['member276single'] = 'B';
    }
}
function &selector276() {
    $receiver276 = new Selected276();
    echo 'C|';
    return $receiver276;
}
function member276() {
    echo 'M|';
    return $GLOBALS['member276single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns276UntypedPairImplicitDefaultSingle\\Selected276::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member276single'] = 'A';
    return true;
});
$get276single = false;
$set276single = false;
$member276single = 'A';
echo 'B|', selector276()::{member276()}, '|', $get276single === true && $set276single === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
