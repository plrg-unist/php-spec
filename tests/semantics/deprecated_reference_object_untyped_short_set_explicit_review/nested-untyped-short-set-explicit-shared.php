<?php
namespace Ns269UntypedShortSetExplicitPeer;
class Leaf269 {
    public function __destruct() {
        echo 'L|';
    }
}
class Middle269 {
    public $pad = true {
        set($innerValue269) => ($GLOBALS['called269peer'] = true) ? $innerValue269 : $innerValue269;
    }
    public $edge;
    public function __construct() {
        $this->edge = $GLOBALS['outside269peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === true ? 'F|' : 'BAD|';
    }
}
class Root269 {
    public $middle;
    public $pad = false {
        set($outerValue269) => ($GLOBALS['called269peer'] = true) ? $outerValue269 : $outerValue269;
    }
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        $this->middle = new Middle269();
        $this->tail = $GLOBALS['outside269peer'];
    }
    public function __destruct() {
        echo 'D|', Root269::A, '|', 'P|';
        $GLOBALS['member269peer'] = 'B';
    }
}
function &selector269() {
    $receiver269 = new Root269();
    echo 'C|';
    return $receiver269;
}
function member269() {
    echo 'M|', $GLOBALS['called269peer'] === false ? 'N|' : 'BAD|';
    return $GLOBALS['member269peer'];
}
function notice269($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns269UntypedShortSetExplicitPeer\\Root269::A is deprecated' || $message === 'Constant Ns269UntypedShortSetExplicitPeer\\Root269::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member269peer'] = 'A';
    return true;
}
$called269peer = false;
$outside269peer = new Leaf269();
$member269peer = 'A';
\set_error_handler('Ns269UntypedShortSetExplicitPeer\\notice269');
echo 'B|', selector269()::{member269()}, '|Z|';
unset($outside269peer);
echo 'E|';
\restore_error_handler();
