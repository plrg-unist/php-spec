<?php
namespace Ns270UntypedSetExplicitPeer;
class Leaf270 {
    public function __destruct() {
        echo 'L|';
    }
}
class Middle270 {
    public $pad = true {
        set($innerValue270) {
            $GLOBALS['called270peer'] = true;
            $this->pad = $innerValue270;
        }
    }
    public $edge;
    public function __construct() {
        $this->edge = $GLOBALS['outside270peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === true ? 'F|' : 'BAD|';
    }
}
class Root270 {
    public $middle;
    public $pad = false {
        set($outerValue270) {
            $GLOBALS['called270peer'] = true;
            $this->pad = $outerValue270;
        }
    }
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        $this->middle = new Middle270();
        $this->tail = $GLOBALS['outside270peer'];
    }
    public function __destruct() {
        echo 'D|', Root270::A, '|', 'P|';
        $GLOBALS['member270peer'] = 'B';
    }
}
function &selector270() {
    $receiver270 = new Root270();
    echo 'C|';
    return $receiver270;
}
function member270() {
    echo 'M|', $GLOBALS['called270peer'] === false ? 'N|' : 'BAD|';
    return $GLOBALS['member270peer'];
}
function notice270($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns270UntypedSetExplicitPeer\\Root270::A is deprecated' || $message === 'Constant Ns270UntypedSetExplicitPeer\\Root270::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member270peer'] = 'A';
    return true;
}
$called270peer = false;
$outside270peer = new Leaf270();
$member270peer = 'A';
\set_error_handler('Ns270UntypedSetExplicitPeer\\notice270');
echo 'B|', selector270()::{member270()}, '|Z|';
unset($outside270peer);
echo 'E|';
\restore_error_handler();
