<?php
class HandlerTick21BoundArg {
    public function __destruct() { echo 'A;'; throw new Exception('handler-bound-tick'); }
}
class HandlerTick21Receiver {
    public function make() { return function (...$args) { echo 'BAD-CALL;'; }; }
    public function __destruct() { echo 'R;'; }
}
function handler_tick21_null($error) { echo 'H;'; return null; }
function handler_review_bound_final($bytes, $phase) {
    $receiver = new HandlerTick21Receiver(); $arg = new HandlerTick21BoundArg();
    $callback = $receiver->make();
    register_tick_function($callback, $arg);
    $receiver = null; $callback = null; $arg = null;
    return $bytes . 'F;';
}
set_exception_handler('handler_tick21_null');
ob_start('handler_review_bound_final');
echo 'B;';
