<?php
#[Deprecated] const X = [];
class Receiver191 {}
$receiver = new Receiver191();
$fn = function($value = X, $tag = 0) { echo $value === [] ? 'E|' : 'BAD|', $tag, '|'; };
set_error_handler(function() { echo 'H|'; return true; });
$fn->call($receiver);
$fn->call($receiver, tag: 7);
$fn(); $fn();
