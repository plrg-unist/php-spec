<?php
namespace Ns242RefProperty;
class Payload242 {
    public function __destruct() {
        echo 'P|';
        $GLOBALS['member242'] = 'B';
    }
}
class Base242 {
    public $payload;
    #[\Deprecated]
    public const A = 7, B = 8;
    public function __destruct() {
        echo 'D|', Child242::A, '|';
    }
}
class Child242 extends Base242 {
    #[\Deprecated]
    public const A = 9, B = 10;
}
function &selector242() {
    $receiver242 = new Child242();
    $receiver242->payload = new Payload242();
    echo 'C|';
    return $receiver242;
}
function member242() {
    echo 'M|';
    return $GLOBALS['member242'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns242RefProperty\\Child242::A is deprecated' || $message === 'Constant Ns242RefProperty\\Child242::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member242'] = 'A';
    return true;
});
$member242 = 'A';
echo 'L|', selector242()::A, '|R|', selector242()::{member242()}, '|Z|';
\restore_error_handler();
