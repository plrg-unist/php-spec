<?php
namespace Ns268UntypedShortSetSingle;
class Selected268 {
    public $tag = 17 {
        set => ($GLOBALS['called268single'] = true) ? 99 : $value;
    }
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === 17 ? 'I|' : 'BAD|';
        $GLOBALS['member268single'] = 'B';
    }
}
function &selector268() {
    $receiver268 = new Selected268();
    echo 'C|';
    return $receiver268;
}
function member268() {
    echo 'M|';
    return $GLOBALS['member268single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns268UntypedShortSetSingle\\Selected268::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member268single'] = 'A';
    return true;
});
$called268single = false;
$member268single = 'A';
echo 'B|', selector268()::{member268()}, '|', $called268single === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
