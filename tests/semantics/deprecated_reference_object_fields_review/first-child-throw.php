<?php
namespace Ns243FieldsThrow;
class First243 {
    public function __destruct() {
        echo 'L|';
        throw $GLOBALS['exception243peer'];
    }
}
class Last243 {
    public function __destruct() {
        echo 'R|';
    }
}
class Base243 {
    public $head;
    public $padding;
    #[\Deprecated]
    public const A = 3;
    public function __destruct() {
        echo 'D|';
    }
}
class Leaf243 extends Base243 {
    public $tail;
    #[\Deprecated]
    public const A = 11;
}
function &selector243peer() {
    $receiver243peer = new Leaf243();
    $receiver243peer->tail = new Last243();
    $receiver243peer->padding = false;
    $receiver243peer->head = new First243();
    echo 'C|';
    return $receiver243peer;
}
function member243peer() {
    echo 'M|';
    return 'A';
}
\set_error_handler(function ($level, $message) {
    echo 'H|';
    return true;
});
$exception243peer = new \Exception('saved');
$value243peer = 71;
try {
    $value243peer = selector243peer()::{\Ns243FieldsThrow\member243peer()};
    echo 'V|';
} catch (\Exception $caught243peer) {
    echo $caught243peer === $exception243peer ? 'S|' : 'BAD|';
}
echo $value243peer, '|Z|';
\restore_error_handler();
