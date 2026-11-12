<?php
namespace Ns251TypedBool;
class Leaf251 {
    public function __destruct() {
        echo 'L|';
    }
}
class Base251 {
    public bool $tag;
}
class Middle251 extends Base251 {
    public $edge;
    public function __destruct() {
        echo 'I|', $this->tag === true ? 'T|' : 'BAD|';
    }
}
class Root251 {
    public $middle;
    public $tail;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', Root251::A, '|';
        $GLOBALS['member251peer'] = 'B';
    }
}
function &selector251() {
    $middle251 = new Middle251();
    $middle251->tag = true;
    $middle251->edge = $GLOBALS['outside251peer'];
    $receiver251 = new Root251();
    $receiver251->middle = $middle251;
    $receiver251->tail = $GLOBALS['outside251peer'];
    echo 'C|';
    return $receiver251;
}
function member251() {
    echo 'M|';
    return $GLOBALS['member251peer'];
}
function notice251($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns251TypedBool\\Root251::A is deprecated' || $message === 'Constant Ns251TypedBool\\Root251::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member251peer'] = 'A';
    return true;
}
$outside251peer = new Leaf251();
$member251peer = 'A';
\set_error_handler('Ns251TypedBool\\notice251');
echo 'B|', selector251()::{member251()}, '|Z|';
unset($outside251peer);
echo 'E|';
\restore_error_handler();
