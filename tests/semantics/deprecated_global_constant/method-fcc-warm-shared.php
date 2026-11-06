<?php
#[Deprecated] const X = [];
class Receiver193 { function read($value = X) { echo $value === [] ? 'E|' : 'BAD|'; } }
$receiver = new Receiver193();
set_error_handler(function() { echo 'H|'; return true; });
$receiver->read(); $fn = $receiver->read(...); $copy = clone $fn;
$receiver = null; $fn(); $fn = null; $copy();
