<?php
namespace Ns280UntypedPairSingle;
trait Tags280 {
    public $tag = 17 {
        set { $GLOBALS['set280single'] = true; $this->tag = $value; }
        get { $GLOBALS['get280single'] = true; return $this->tag; }
    }
}
class Selected280 {
    use Tags280;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === 17 ? 'I|' : 'BAD|';
        $GLOBALS['member280single'] = 'B';
    }
}
function &selector280() {
    $receiver280 = new Selected280();
    echo 'C|';
    return $receiver280;
}
function member280() {
    echo 'M|';
    return $GLOBALS['member280single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns280UntypedPairSingle\\Selected280::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member280single'] = 'A';
    return true;
});
$get280single = false;
$set280single = false;
$member280single = 'A';
echo 'B|', selector280()::{member280()}, '|', $get280single === true && $set280single === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
