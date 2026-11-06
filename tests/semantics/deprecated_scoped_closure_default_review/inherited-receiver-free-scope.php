<?php
#[Deprecated] const X = [];
class Base192 {
    public static function make() { return function($value = X) { echo static::class, '|'; }; }
}
class Child192 extends Base192 {}
$fn = Child192::make();
$copy = clone $fn;
set_error_handler(function() { echo 'H|'; return true; });
$fn(); $copy();
