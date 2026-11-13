<?php
namespace Ns273UntypedTraitImplicitSetPeer;
class Leaf273 {
    public function __destruct() {
        echo 'L|';
    }
}
class Middle273 {
    public $pad = true;
    public $edge;
    public function __construct() {
        $this->edge = $GLOBALS['outside273peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === true ? 'F|' : 'BAD|';
    }
}
trait RootPad273 {
    public $pad = false {
        set {
            $GLOBALS['called273peer'] = true;
            $this->pad = $value;
        }
    }
}
class Root273 {
    public $middle;
    use RootPad273;
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        $this->middle = new Middle273();
        $this->tail = $GLOBALS['outside273peer'];
    }
    public function __destruct() {
        echo 'D|', Root273::A, '|', 'P|';
        $GLOBALS['member273peer'] = 'B';
    }
}
function &selector273() {
    $receiver273 = new Root273();
    echo 'C|';
    return $receiver273;
}
function member273() {
    echo 'M|', $GLOBALS['called273peer'] === false ? 'N|' : 'BAD|';
    return $GLOBALS['member273peer'];
}
function notice273($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns273UntypedTraitImplicitSetPeer\\Root273::A is deprecated' || $message === 'Constant Ns273UntypedTraitImplicitSetPeer\\Root273::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member273peer'] = 'A';
    return true;
}
$called273peer = false;
$outside273peer = new Leaf273();
$member273peer = 'A';
\set_error_handler('Ns273UntypedTraitImplicitSetPeer\\notice273');
echo 'B|', selector273()::{member273()}, '|Z|';
unset($outside273peer);
echo 'E|';
\restore_error_handler();
