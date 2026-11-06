<?php
#[Deprecated] const X = [];
class Changed192 {}
class Quiet192 {}
class Receiver192 {
    public function make() { return function($value = X) { echo 'E|'; return 7; }; }
    public function __destruct() {
        global $other;
        echo 'R|'; $other(); echo 'Z|';
    }
}
$receiver = new Receiver192(); $original = $receiver->make();
$fn = $original->bindTo($receiver, Changed192::class);
$original = $receiver = null;
set_error_handler(function() { echo 'H|'; return true; });
echo $fn(), '|';
$other = $fn->bindTo(new Quiet192(), Changed192::class);
$fn = null;
$other = null;
echo 'D|';
