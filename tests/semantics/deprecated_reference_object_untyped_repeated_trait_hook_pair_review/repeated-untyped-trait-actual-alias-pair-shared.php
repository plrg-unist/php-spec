<?php
namespace Ns282RepeatedTraitActualPairPeer;
use Ns282RepeatedTraitActualPairPeer\RootPad282 as RepeatedPad282;
class Leaf282 {
    public function __destruct() {
        echo 'L|';
    }
}
class Middle282 {
    public $pad = true;
    public $edge;
    public function __construct() {
        $this->edge = $GLOBALS['outside282peer'];
    }
    public function __destruct() {
        echo 'I|', $this->pad === true ? 'F|' : 'BAD|';
    }
}
trait RootPad282 {
    public $pad {
        set($incoming) => ($GLOBALS['set282peer'] = true) ? $incoming : $incoming;
        get => ($GLOBALS['get282peer'] = true) ? $this->pad : $this->pad;
    }
}
class Parent282 {
    public $anchor = 31;
}
class Root282 extends Parent282 {
    use RootPad282;
    use RepeatedPad282;
    public $middle;
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __construct() {
        echo $this->anchor === 31 && $this->pad === null && $GLOBALS['get282peer'] === true && $GLOBALS['set282peer'] === false ? 'Q|' : 'BAD|';
        $GLOBALS['get282peer'] = false;
        $this->middle = new Middle282();
        $this->tail = $GLOBALS['outside282peer'];
    }
    public function __destruct() {
        echo $this->anchor === 31 ? 'R|' : 'BAD|';
        echo 'D|', Root282::A, '|', 'P|';
        $GLOBALS['member282peer'] = 'B';
    }
}
function &selector282() {
    $receiver282 = new Root282();
    echo 'C|';
    return $receiver282;
}
function member282() {
    echo 'M|', ($GLOBALS['set282peer'] === false && $GLOBALS['get282peer'] === false) ? 'N|' : 'BAD|';
    return $GLOBALS['member282peer'];
}
function notice282($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns282RepeatedTraitActualPairPeer\\Root282::A is deprecated' || $message === 'Constant Ns282RepeatedTraitActualPairPeer\\Root282::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member282peer'] = 'A';
    return true;
}
$set282peer = false;
$get282peer = false;
$outside282peer = new Leaf282();
$member282peer = 'A';
\set_error_handler('Ns282RepeatedTraitActualPairPeer\\notice282');
echo 'B|', selector282()::{member282()}, '|Z|';
unset($outside282peer);
echo 'E|';
\restore_error_handler();
