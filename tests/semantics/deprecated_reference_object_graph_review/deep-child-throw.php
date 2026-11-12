<?php
namespace Ns244DeepThrow;
class Deep244 {
    public function __destruct() {
        echo 'G|';
        throw $GLOBALS['exception244peer'];
    }
}
class Middle244 {
    public $child;
    public function __destruct() {
        echo 'I|';
    }
}
class Last244 {
    public function __destruct() {
        echo 'R|';
    }
}
class Base244 {
    public $first;
    public $padding;
    #[\Deprecated]
    public const A = 3;
    public function __destruct() {
        echo 'D|';
    }
}
class Root244 extends Base244 {
    public $tail;
    #[\Deprecated]
    public const A = 11;
}
function &selector244peer() {
    $receiver244peer = new Root244();
    $receiver244peer->tail = new Last244();
    $middle244peer = new Middle244();
    $middle244peer->child = new Deep244();
    $receiver244peer->first = $middle244peer;
    $receiver244peer->padding = false;
    unset($middle244peer);
    echo 'C|';
    return $receiver244peer;
}
function member244peer() {
    echo 'M|';
    return 'A';
}
\set_error_handler(function ($level, $message) {
    echo 'H|';
    return true;
});
$exception244peer = new \Exception('saved');
$value244peer = 71;
try {
    $value244peer = selector244peer()::{\Ns244DeepThrow\member244peer()};
    echo 'V|';
} catch (\Exception $caught244peer) {
    echo $caught244peer === $exception244peer ? 'S|' : 'BAD|';
}
echo $value244peer, '|Z|';
\restore_error_handler();
