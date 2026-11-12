<?php
namespace Ns255NullablePeer;
class Leaf255 {
    public function __destruct() {
        echo 'L|';
    }
}
class Base255 {
    public null|bool $tag;
}
class Middle255 extends Base255 {
    public $edge;
    public function __destruct() {
        echo 'I|', $this->tag === true ? 'T|' : 'BAD|';
    }
}
class Root255 {
    public $middle;
    public $tail;
    public null|string $label;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', Root255::A, '|', $this->label === 'req255' ? 'S|' : 'BAD|';
        $GLOBALS['member255peer'] = 'B';
    }
}
function &selector255() {
    $middle255 = new Middle255();
    $middle255->tag = true;
    $middle255->edge = $GLOBALS['outside255peer'];
    $receiver255 = new Root255();
    $receiver255->middle = $middle255;
    $receiver255->tail = $GLOBALS['outside255peer'];
    $suffix255 = '255';
    $receiver255->label = 'req' . $suffix255;
    echo 'C|';
    return $receiver255;
}
function member255() {
    echo 'M|';
    return $GLOBALS['member255peer'];
}
function notice255($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns255NullablePeer\\Root255::A is deprecated' || $message === 'Constant Ns255NullablePeer\\Root255::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member255peer'] = 'A';
    return true;
}
$outside255peer = new Leaf255();
$member255peer = 'A';
\set_error_handler('Ns255NullablePeer\\notice255');
echo 'B|', selector255()::{member255()}, '|Z|';
unset($outside255peer);
echo 'E|';
\restore_error_handler();
