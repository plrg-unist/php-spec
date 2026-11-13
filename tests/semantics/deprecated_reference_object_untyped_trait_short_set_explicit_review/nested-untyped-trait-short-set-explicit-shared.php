<?php
namespace Ns272UntypedTraitShortSetExplicitPeer;
class Leaf272 {
    public function __destruct() {
        echo 'L|';
    }
}
class Middle272 {
    public $pad = true;
    public $edge;
    public function __construct() {
        $this->edge = $GLOBALS['outside272peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === true ? 'F|' : 'BAD|';
    }
}
trait RootPad272 {
    public $pad = false {
        set($traitValue272) => ($GLOBALS['called272peer'] = true) ? $traitValue272 : $traitValue272;
    }
}
class Root272 {
    public $middle;
    use RootPad272;
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        $this->middle = new Middle272();
        $this->tail = $GLOBALS['outside272peer'];
    }
    public function __destruct() {
        echo 'D|', Root272::A, '|', 'P|';
        $GLOBALS['member272peer'] = 'B';
    }
}
function &selector272() {
    $receiver272 = new Root272();
    echo 'C|';
    return $receiver272;
}
function member272() {
    echo 'M|', $GLOBALS['called272peer'] === false ? 'N|' : 'BAD|';
    return $GLOBALS['member272peer'];
}
function notice272($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns272UntypedTraitShortSetExplicitPeer\\Root272::A is deprecated' || $message === 'Constant Ns272UntypedTraitShortSetExplicitPeer\\Root272::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member272peer'] = 'A';
    return true;
}
$called272peer = false;
$outside272peer = new Leaf272();
$member272peer = 'A';
\set_error_handler('Ns272UntypedTraitShortSetExplicitPeer\\notice272');
echo 'B|', selector272()::{member272()}, '|Z|';
unset($outside272peer);
echo 'E|';
\restore_error_handler();
