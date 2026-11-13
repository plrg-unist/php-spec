<?php
namespace Ns274UntypedTraitImplicitShortSetPeer;
class Leaf274 {
    public function __destruct() {
        echo 'L|';
    }
}
class Middle274 {
    public $pad = true;
    public $edge;
    public function __construct() {
        $this->edge = $GLOBALS['outside274peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === true ? 'F|' : 'BAD|';
    }
}
trait RootPad274 {
    public $pad = false {
        set => ($GLOBALS['called274peer'] = true) ? $value : $value;
    }
}
class Root274 {
    public $middle;
    use RootPad274;
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        $this->middle = new Middle274();
        $this->tail = $GLOBALS['outside274peer'];
    }
    public function __destruct() {
        echo 'D|', Root274::A, '|', 'P|';
        $GLOBALS['member274peer'] = 'B';
    }
}
function &selector274() {
    $receiver274 = new Root274();
    echo 'C|';
    return $receiver274;
}
function member274() {
    echo 'M|', $GLOBALS['called274peer'] === false ? 'N|' : 'BAD|';
    return $GLOBALS['member274peer'];
}
function notice274($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns274UntypedTraitImplicitShortSetPeer\\Root274::A is deprecated' || $message === 'Constant Ns274UntypedTraitImplicitShortSetPeer\\Root274::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member274peer'] = 'A';
    return true;
}
$called274peer = false;
$outside274peer = new Leaf274();
$member274peer = 'A';
\set_error_handler('Ns274UntypedTraitImplicitShortSetPeer\\notice274');
echo 'B|', selector274()::{member274()}, '|Z|';
unset($outside274peer);
echo 'E|';
\restore_error_handler();
