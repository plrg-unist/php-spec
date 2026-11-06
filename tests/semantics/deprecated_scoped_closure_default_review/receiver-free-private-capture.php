<?php
#[Deprecated] const X = [];
class Changed192 {}
class Held192 { public function __destruct() { echo 'C|'; } }
class Base192 {
    public static function make($held) {
        return function($value = X) use ($held) { echo static::class, '|'; return 7; };
    }
}
$held = new Held192(); $original = Base192::make($held);
$fn = $original->bindTo(null, Changed192::class);
$held = $original = null;
set_error_handler(function() { global $fn; echo 'H|'; $fn = null; return true; });
$result = $fn();
echo $result, '|';
