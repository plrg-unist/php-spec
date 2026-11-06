<?php
namespace {
#[Deprecated] const X = [];
function notice187($level, $message) {
    echo 'H|';
    define('Ns187Reentry\\X', 9);
    \Ns187Reentry\Child187::receive();
    return true;
}
}
namespace Ns187Reentry {
class Base187 { public static function receive($value = X) { echo $value === 9 ? 'N|' : 'E|'; } }
class Child187 extends Base187 {}
set_error_handler('notice187');
Child187::receive();
Base187::receive();
}
