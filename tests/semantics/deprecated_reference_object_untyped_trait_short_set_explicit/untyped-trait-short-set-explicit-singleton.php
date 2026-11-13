<?php
namespace Ns272UntypedTraitShortSetExplicitSingle;
trait Tag272 {
    public $tag = 17 {
        set($incoming272) => ($GLOBALS['called272single'] = true) ? 99 : $incoming272;
    }
}
class Selected272 {
    use Tag272;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === 17 ? 'I|' : 'BAD|';
        $GLOBALS['member272single'] = 'B';
    }
}
function &selector272() {
    $receiver272 = new Selected272();
    echo 'C|';
    return $receiver272;
}
function member272() {
    echo 'M|';
    return $GLOBALS['member272single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns272UntypedTraitShortSetExplicitSingle\\Selected272::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member272single'] = 'A';
    return true;
});
$called272single = false;
$member272single = 'A';
echo 'B|', selector272()::{member272()}, '|', $called272single === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
