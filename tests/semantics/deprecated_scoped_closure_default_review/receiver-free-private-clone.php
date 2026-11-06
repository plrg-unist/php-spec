<?php
#[Deprecated] const X = [];
class Changed192 {}
class Base192 {
    public static function make() { return function($value = X) { echo static::class, '|'; }; }
}
$original = Base192::make();
$fn = $original->bindTo(null, Changed192::class);
$original = null;
set_error_handler(function() { echo 'H|'; return true; });
$fn();
$copy = clone $fn;
$fn = null;
$copy();
$copy = null;
echo 'D|';
