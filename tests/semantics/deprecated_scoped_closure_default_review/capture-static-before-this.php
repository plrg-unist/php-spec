<?php
#[Deprecated] const X = [];
class Changed192 {}
class Captured192 { public function __destruct() { echo 'C|'; } }
class Static192 { public function __destruct() { echo 'S|'; } }
class Receiver192 {
    public function make($held) {
        return function($value = X) use ($held) {
            static $slot = null;
            if ($slot === null) { $slot = new Static192(); }
            echo $this instanceof Receiver192 ? 'E|' : 'BAD|';
            return 7;
        };
    }
    public function __destruct() { echo 'R|'; }
}
$receiver = new Receiver192(); $held = new Captured192();
$original = $receiver->make($held);
$fn = $original->bindTo($receiver, Changed192::class);
$held = $original = $receiver = null;
set_error_handler(function() { global $fn; echo 'H|'; $fn = null; return true; });
$result = $fn();
echo $result, '|';
