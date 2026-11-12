<?php
namespace Ns242PropertyThrow;
class Tail242 {
    public function __destruct() {
        echo 'P|';
        throw $GLOBALS['exception242peer'];
    }
}
class Base242 {
    public $link;
    #[\Deprecated]
    public const A = 3;
    public function __destruct() {
        echo 'D|';
    }
}
class Leaf242 extends Base242 {
    #[\Deprecated]
    public const A = 11;
}
function &selector242peer() {
    $receiver242peer = new Leaf242();
    $receiver242peer->link = new Tail242();
    echo 'C|';
    return $receiver242peer;
}
function member242peer() {
    echo 'M|';
    return 'A';
}
\set_error_handler(function ($level, $message) {
    echo 'H|';
    return true;
});
$exception242peer = new \Exception('saved');
$value242peer = 71;
try {
    $value242peer = selector242peer()::{\Ns242PropertyThrow\member242peer()};
    echo 'V|';
} catch (\Exception $caught242peer) {
    echo $caught242peer === $exception242peer ? 'S|' : 'BAD|';
}
echo $value242peer, '|Z|';
\restore_error_handler();
