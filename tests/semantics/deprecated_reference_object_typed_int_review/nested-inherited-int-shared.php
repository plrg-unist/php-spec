<?php
namespace Ns250TypedInt;
class Leaf250 {
    public function __destruct() {
        echo 'L|';
    }
}
class Base250 {
    public int $tag;
}
class Middle250 extends Base250 {
    public $edge;
    public function __destruct() {
        echo 'I|', $this->tag === 17 ? 'T|' : 'BAD|';
    }
}
class Root250 {
    public $middle;
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', Root250::A, '|';
        $GLOBALS['member250peer'] = 'B';
    }
}
function &selector250() {
    $middle250 = new Middle250();
    $middle250->tag = 17;
    $middle250->edge = $GLOBALS['outside250peer'];
    $receiver250 = new Root250();
    $receiver250->middle = $middle250;
    $receiver250->tail = $GLOBALS['outside250peer'];
    echo 'C|';
    return $receiver250;
}
function member250() {
    echo 'M|';
    return $GLOBALS['member250peer'];
}
function notice250($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns250TypedInt\\Root250::A is deprecated' || $message === 'Constant Ns250TypedInt\\Root250::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member250peer'] = 'A';
    return true;
}
$outside250peer = new Leaf250();
$member250peer = 'A';
\set_error_handler('Ns250TypedInt\\notice250');
echo 'B|', selector250()::{member250()}, '|Z|';
unset($outside250peer);
echo 'E|';
\restore_error_handler();
