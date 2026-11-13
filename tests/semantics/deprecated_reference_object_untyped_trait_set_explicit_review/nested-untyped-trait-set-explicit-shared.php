<?php
namespace Ns271UntypedTraitSetExplicitPeer;
class Leaf271 {
    public function __destruct() {
        echo 'L|';
    }
}
class Middle271 {
    public $pad = true;
    public $edge;
    public function __construct() {
        $this->edge = $GLOBALS['outside271peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === true ? 'F|' : 'BAD|';
    }
}
trait RootPad271 {
    public $pad = false {
        set($traitValue271) {
            $GLOBALS['called271peer'] = true;
            $this->pad = $traitValue271;
        }
    }
}
class Root271 {
    public $middle;
    use RootPad271;
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        $this->middle = new Middle271();
        $this->tail = $GLOBALS['outside271peer'];
    }
    public function __destruct() {
        echo 'D|', Root271::A, '|', 'P|';
        $GLOBALS['member271peer'] = 'B';
    }
}
function &selector271() {
    $receiver271 = new Root271();
    echo 'C|';
    return $receiver271;
}
function member271() {
    echo 'M|', $GLOBALS['called271peer'] === false ? 'N|' : 'BAD|';
    return $GLOBALS['member271peer'];
}
function notice271($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns271UntypedTraitSetExplicitPeer\\Root271::A is deprecated' || $message === 'Constant Ns271UntypedTraitSetExplicitPeer\\Root271::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member271peer'] = 'A';
    return true;
}
$called271peer = false;
$outside271peer = new Leaf271();
$member271peer = 'A';
\set_error_handler('Ns271UntypedTraitSetExplicitPeer\\notice271');
echo 'B|', selector271()::{member271()}, '|Z|';
unset($outside271peer);
echo 'E|';
\restore_error_handler();
