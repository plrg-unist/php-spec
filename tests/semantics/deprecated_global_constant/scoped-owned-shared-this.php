<?php
#[Deprecated] const X = [];
class Receiver192 {
    public int $tag = 7;
    function make() { return function($value = X, $tag = 0) { echo $value === [] ? 'E|' : 'BAD|', $this->tag, '|', $tag, '|'; }; }
}
$receiver = new Receiver192(); $fn = $receiver->make(); $receiver = null;
set_error_handler(function() { echo 'H|'; return true; });
$fn(); $fn(tag: 2); $copy = clone $fn; $fn = null; $copy(); $copy = null;
