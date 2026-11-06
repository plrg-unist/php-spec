<?php
#[Deprecated] const X = [];
class Receiver191 {
    static function make() { return function($value = X) { echo $value === [] ? 'E|' : 'BAD|'; }; }
}
$receiver = new Receiver191(); $fn = Receiver191::make();
set_error_handler(function() { echo 'H|'; return true; });
$fn->call($receiver); $fn->call($receiver);
