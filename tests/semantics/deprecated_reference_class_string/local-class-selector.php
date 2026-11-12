<?php
namespace Ns240Ref;
class Base240 {
    #[\Deprecated]
    public const A = 7;
}
class Child240 extends Base240 {
    #[\Deprecated]
    public const A = 9;
}
function &selector240() {
    $class240 = 'Ns240Ref\\Child240';
    echo 'C|';
    return $class240;
}
function member240() {
    echo 'M|';
    return 'A';
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns240Ref\\Child240::A is deprecated' ? 'H|' : 'BAD|';
    return true;
});
echo 'L|', selector240()::A, '|R|', selector240()::{member240()}, '|Z|';
\restore_error_handler();
