<?php
namespace Ns274UntypedTraitImplicitShortSetSingle;
trait Tag274 {
    public $tag = 17 {
        set => ($GLOBALS['called274single'] = true) ? 99 : $value;
    }
}
class Selected274 {
    use Tag274;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === 17 ? 'I|' : 'BAD|';
        $GLOBALS['member274single'] = 'B';
    }
}
function &selector274() {
    $receiver274 = new Selected274();
    echo 'C|';
    return $receiver274;
}
function member274() {
    echo 'M|';
    return $GLOBALS['member274single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns274UntypedTraitImplicitShortSetSingle\\Selected274::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member274single'] = 'A';
    return true;
});
$called274single = false;
$member274single = 'A';
echo 'B|', selector274()::{member274()}, '|', $called274single === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
