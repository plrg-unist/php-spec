<?php
namespace Ns273UntypedTraitImplicitSetSingle;
trait Tag273 {
    public $tag = 17 {
        set {
            $GLOBALS['called273single'] = true;
            $this->tag = $value;
        }
    }
}
class Selected273 {
    use Tag273;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === 17 ? 'I|' : 'BAD|';
        $GLOBALS['member273single'] = 'B';
    }
}
function &selector273() {
    $receiver273 = new Selected273();
    echo 'C|';
    return $receiver273;
}
function member273() {
    echo 'M|';
    return $GLOBALS['member273single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns273UntypedTraitImplicitSetSingle\\Selected273::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member273single'] = 'A';
    return true;
});
$called273single = false;
$member273single = 'A';
echo 'B|', selector273()::{member273()}, '|', $called273single === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
