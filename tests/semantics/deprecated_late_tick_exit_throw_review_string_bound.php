<?php
class ExitThrow20BoundArg {
    public function __destruct() { echo 'A;'; throw new Exception('string-exit-tick-failure'); }
}
class ExitThrow20Receiver {
    public function make() { return function (...$args) { echo 'BAD-CALL;'; }; }
    public function __destruct() { echo 'R;'; }
}
function exit_throw_review_bound_final($bytes, $phase) {
    $receiver = new ExitThrow20Receiver(); $arg = new ExitThrow20BoundArg();
    $callback = $receiver->make();
    register_tick_function($callback, $arg);
    $receiver = null; $callback = null; $arg = null;
    return $bytes . 'F;';
}
ob_start('exit_throw_review_bound_final');
echo 'B;';
exit('E;');
