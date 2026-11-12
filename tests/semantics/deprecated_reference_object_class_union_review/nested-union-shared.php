<?php
namespace Ns258ClassUnionPeer;
class LeafBase258 {
    public function __destruct() {
        echo 'L|';
    }
}
class LeafChild258 extends LeafBase258 {
}
class Base258 {
    public $pad;
    public LeafBase258|int|NotLoaded258 $edge;
}
class Middle258 extends Base258 {
    public function __destruct() {
        echo 'I|', $this->pad === false ? 'F|' : 'BAD|';
        echo $this->edge === $GLOBALS['outside258peer'] ? 'S|' : 'BAD|';
    }
}
class Root258 {
    public NotLoaded258|LeafBase258|Middle258 $middle;
    public null|NotLoaded258|LeafBase258 $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', Root258::A, '|';
        $GLOBALS['member258peer'] = 'B';
    }
}
function &selector258() {
    $middle258 = new Middle258();
    $middle258->pad = false;
    $middle258->edge = $GLOBALS['outside258peer'];
    $receiver258 = new Root258();
    $receiver258->middle = $middle258;
    $receiver258->tail = $GLOBALS['outside258peer'];
    echo 'C|';
    return $receiver258;
}
function member258() {
    echo 'M|';
    return $GLOBALS['member258peer'];
}
function notice258($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns258ClassUnionPeer\\Root258::A is deprecated' || $message === 'Constant Ns258ClassUnionPeer\\Root258::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member258peer'] = 'A';
    return true;
}
$outside258peer = new LeafChild258();
$member258peer = 'A';
\set_error_handler('Ns258ClassUnionPeer\\notice258');
echo 'B|', selector258()::{member258()}, '|Z|';
unset($outside258peer);
echo 'E|';
\restore_error_handler();
