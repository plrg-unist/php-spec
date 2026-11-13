<?php
namespace Ns286AutomaticShortSetClassImplicitPairPeer;
class Leaf286 {
    public function __destruct() {
        echo 'L|';
    }
}
class PadLeaf286 {
    public function __destruct() {
        echo 'U|';
    }
}
class Middle286 {
    public $pad = true;
    public $edge;
    public function __construct() {
        $this->edge = $GLOBALS['outside286peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === true ? 'F|' : 'BAD|';
    }
}
class Root286 {
    public $anchor = 31;
    public $middle;
    public $tail;
    public $pad {
        set => ($GLOBALS['set286peer'] = true) ? $value : $value;
        get {
            $GLOBALS['get286peer'] = true;
            return 7;
        }
    }
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        echo $this->anchor === 31 && $this->pad === 7 && $GLOBALS['get286peer'] === true && $GLOBALS['set286peer'] === false ? 'Q|' : 'BAD|';
        $GLOBALS['get286peer'] = false;
        $this->pad = new PadLeaf286();
        echo $GLOBALS['set286peer'] === true ? 'S|' : 'BAD|';
        $GLOBALS['set286peer'] = false;
        $this->middle = new Middle286();
        $this->tail = $GLOBALS['outside286peer'];
    }
    public function __destruct() {
        echo $this->anchor === 31 ? 'R|' : 'BAD|';
        echo 'D|', Root286::A, '|', 'P|';
        $GLOBALS['member286peer'] = 'B';
    }
}
function &selector286() {
    $receiver286 = new Root286();
    echo 'C|';
    return $receiver286;
}
function member286() {
    echo 'M|', ($GLOBALS['set286peer'] === false && $GLOBALS['get286peer'] === false) ? 'N|' : 'BAD|';
    return $GLOBALS['member286peer'];
}
function notice286($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns286AutomaticShortSetClassImplicitPairPeer\\Root286::A is deprecated' || $message === 'Constant Ns286AutomaticShortSetClassImplicitPairPeer\\Root286::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member286peer'] = 'A';
    return true;
}
$set286peer = false;
$get286peer = false;
$outside286peer = new Leaf286();
$member286peer = 'A';
\set_error_handler('Ns286AutomaticShortSetClassImplicitPairPeer\\notice286');
echo 'B|', selector286()::{member286()}, '|Z|';
unset($outside286peer);
echo 'E|';
\restore_error_handler();
