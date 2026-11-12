<?php
namespace Ns260NominalDnfPeer;
interface IBase260 {}
interface ISecond260 {}
interface IInherited260 extends IBase260 {}
interface IView260 {}
class LeafBase260 implements IInherited260, ISecond260 {
    public function __destruct() {
        echo 'L|';
    }
}
class LeafChild260 extends LeafBase260 {
}
class Base260 {
    public $pad;
    public (IBase260&ISecond260)|int $edge;
}
class Middle260 extends Base260 implements IView260 {
    public function __destruct() {
        echo 'I|', $this->pad === false ? 'F|' : 'BAD|';
        echo $this->edge === $GLOBALS['outside260peer'] ? 'S|' : 'BAD|';
    }
}
class Root260 {
    public LeafBase260|IView260 $middle;
    public NotLoaded260|(ISecond260&IBase260) $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', Root260::A, '|';
        $GLOBALS['member260peer'] = 'B';
    }
}
function &selector260() {
    $middle260 = new Middle260();
    $middle260->pad = false;
    $middle260->edge = $GLOBALS['outside260peer'];
    $receiver260 = new Root260();
    $receiver260->middle = $middle260;
    $receiver260->tail = $GLOBALS['outside260peer'];
    echo 'C|';
    return $receiver260;
}
function member260() {
    echo 'M|';
    return $GLOBALS['member260peer'];
}
function notice260($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns260NominalDnfPeer\\Root260::A is deprecated' || $message === 'Constant Ns260NominalDnfPeer\\Root260::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member260peer'] = 'A';
    return true;
}
$outside260peer = new LeafChild260();
$member260peer = 'A';
\set_error_handler('Ns260NominalDnfPeer\\notice260');
echo 'B|', selector260()::{member260()}, '|Z|';
unset($outside260peer);
echo 'E|';
\restore_error_handler();
