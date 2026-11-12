<?php
namespace Ns241RefObject;
class Base241 {
    #[\Deprecated]
    public const A = 7, B = 8;
    public function __destruct() {
        echo 'D|', Child241::A, '|';
        $GLOBALS['member241'] = 'B';
    }
}
class Child241 extends Base241 {
    #[\Deprecated]
    public const A = 9, B = 10;
}
function &selector241() {
    $receiver241 = new Child241();
    echo 'C|';
    return $receiver241;
}
function member241() {
    echo 'M|';
    return $GLOBALS['member241'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && ($message === 'Constant Ns241RefObject\\Child241::A is deprecated' || $message === 'Constant Ns241RefObject\\Child241::B is deprecated') ? 'H|' : 'BAD|';
    $GLOBALS['member241'] = 'A';
    return true;
});
$member241 = 'A';
echo 'L|', selector241()::A, '|R|', selector241()::{member241()}, '|Z|';
\restore_error_handler();
