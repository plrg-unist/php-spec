<?php
namespace {
#[Deprecated] const X = [1];
class Receiver191 {}
function invoke191($fn, $receiver) { $fn->call($receiver); }
function notice191() {
    global $fn, $receiver;
    echo 'H|'; define('Ns191\\X', 9); invoke191($fn, $receiver); return true;
}
}
namespace Ns191 {
$receiver = new \Receiver191();
$fn = function($value = X) { echo $value === 9 ? 'N|' : 'E|'; };
set_error_handler('notice191');
\invoke191($fn, $receiver); \invoke191($fn, $receiver);
}
