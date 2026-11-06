<?php
#[Deprecated] const X = [];
class Receiver191 {
    public function method191($value = X) { echo 'E|'; }
}
$receiver = new Receiver191();
$fake = $receiver->method191(...);
set_error_handler(function() { echo 'H|'; return true; });
$fake->call($receiver);
$fake->call($receiver);
