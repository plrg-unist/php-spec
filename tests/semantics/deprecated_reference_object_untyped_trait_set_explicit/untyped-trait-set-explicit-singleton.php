<?php
namespace Ns271UntypedTraitSetExplicitSingle;
trait Tag271 {
    public $tag = 17 {
        set($incoming271) {
            $GLOBALS['called271single'] = true;
            $this->tag = $incoming271;
        }
    }
}
class Selected271 {
    use Tag271;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === 17 ? 'I|' : 'BAD|';
        $GLOBALS['member271single'] = 'B';
    }
}
function &selector271() {
    $receiver271 = new Selected271();
    echo 'C|';
    return $receiver271;
}
function member271() {
    echo 'M|';
    return $GLOBALS['member271single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns271UntypedTraitSetExplicitSingle\\Selected271::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member271single'] = 'A';
    return true;
});
$called271single = false;
$member271single = 'A';
echo 'B|', selector271()::{member271()}, '|', $called271single === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
