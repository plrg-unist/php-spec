<?php
#[Deprecated] const X = [];
class Base193 { static function read($value = X) { echo static::class, '|'; } }
class Child193 extends Base193 {}
$fn = Closure::fromCallable('Child193::read');
set_error_handler(function() { echo 'H|'; return true; });
$fn(); $fn(); $copy = clone $fn; $fn = null; $copy(); $copy = null;
