<?php
#[Deprecated] const X = [];
class Receiver193 { public int $tag = 7; function read($value = X, $tag = 0) { echo $value === [] ? 'E|' : 'BAD|', $this->tag, '|', $tag, '|'; } }
$receiver = new Receiver193(); $fn = $receiver->read(...); $early = clone $fn;
set_error_handler(function() { echo 'H|'; return true; });
$fn(); $early(tag: 2); $copy = clone $fn; $copy(); $receiver->read(); $fn();
