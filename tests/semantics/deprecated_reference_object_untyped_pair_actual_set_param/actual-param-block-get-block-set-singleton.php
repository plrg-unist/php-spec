<?php
namespace Ns279UntypedPairActualParamSingle;
class Selected279 {
    public $tag = 17 {
        set($incoming279single) { $GLOBALS['set279single'] = true; $this->tag = $incoming279single; }
        get { $GLOBALS['get279single'] = true; return $this->tag; }
    }
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === 17 ? 'I|' : 'BAD|';
        $GLOBALS['member279single'] = 'B';
    }
}
function &selector279() {
    $receiver279 = new Selected279();
    echo 'C|';
    return $receiver279;
}
function member279() {
    echo 'M|';
    return $GLOBALS['member279single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns279UntypedPairActualParamSingle\\Selected279::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member279single'] = 'A';
    return true;
});
$get279single = false;
$set279single = false;
$member279single = 'A';
echo 'B|', selector279()::{member279()}, '|', $get279single === true && $set279single === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
