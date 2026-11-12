<?php
namespace Ns256PrimitiveUnionPeer;
class Leaf256 {
    public function __destruct() {
        echo 'L|';
    }
}
class Base256 {
    public false|int|float $tag;
}
class Middle256 extends Base256 {
    public $edge;
    public function __destruct() {
        echo 'I|', $this->tag === false ? 'F|' : 'BAD|';
    }
}
class Root256 {
    public $middle;
    public $tail;
    public null|bool|float|int|string $label;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', Root256::A, '|', $this->label === 'req256' ? 'S|' : 'BAD|';
        $GLOBALS['member256peer'] = 'B';
    }
}
function &selector256() {
    $middle256 = new Middle256();
    $middle256->tag = false;
    $middle256->edge = $GLOBALS['outside256peer'];
    $receiver256 = new Root256();
    $receiver256->middle = $middle256;
    $receiver256->tail = $GLOBALS['outside256peer'];
    $suffix256 = '256';
    $receiver256->label = 'req' . $suffix256;
    echo 'C|';
    return $receiver256;
}
function member256() {
    echo 'M|';
    return $GLOBALS['member256peer'];
}
function notice256($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns256PrimitiveUnionPeer\\Root256::A is deprecated' || $message === 'Constant Ns256PrimitiveUnionPeer\\Root256::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member256peer'] = 'A';
    return true;
}
$outside256peer = new Leaf256();
$member256peer = 'A';
\set_error_handler('Ns256PrimitiveUnionPeer\\notice256');
echo 'B|', selector256()::{member256()}, '|Z|';
unset($outside256peer);
echo 'E|';
\restore_error_handler();
