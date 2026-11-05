<?php
class BoundTick17Arg { public function __destruct() { echo 'A;'; } }
class BoundTick17Receiver {
    public function make() { return function (...$args) { echo 'BAD-CALL;'; }; }
    public function __destruct() { echo 'R;'; }
}
function callables_review_bound_final($bytes, $phase) {
    $receiver = new BoundTick17Receiver(); $arg = new BoundTick17Arg();
    $callback = $receiver->make();
    register_tick_function($callback, $arg);
    $receiver = null; $callback = null; $arg = null;
    return $bytes . 'F;';
}
ob_start('callables_review_bound_final');
echo 'B;';
