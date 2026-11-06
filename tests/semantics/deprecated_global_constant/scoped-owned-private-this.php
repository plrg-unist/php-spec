<?php
#[Deprecated] const X = [];
class Receiver192 { public int $tag = 7; }
$first = new Receiver192(); $second = new Receiver192(); $second->tag = 9;
$original = function($value = X, $tag = 0) { echo $value === [] ? 'E|' : 'BAD|', $this->tag, '|', $tag, '|'; };
$fn = $original->bindTo($first, Receiver192::class);
set_error_handler(function() { echo 'H|'; return true; });
$fn(); $fn(tag: 2); $copy = clone $fn; $fn = null; $copy();
$other = Closure::bind($original, $second, Receiver192::class);
$original = $first = $second = null; $other(); $other(); $copy = $other = null;
