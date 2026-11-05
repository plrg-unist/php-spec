<?php
class StringExitTickArg { public function __destruct() { echo 'A;'; } }
class StringExitTickReceiver {
    public function make() { return function (...$args) { echo 'BAD-CALL;'; }; }
    public function __destruct() { echo 'R;'; }
}
function exit_review_string_bound_final($bytes, $phase) {
    $receiver = new StringExitTickReceiver(); $arg = new StringExitTickArg();
    $callback = $receiver->make();
    register_tick_function($callback, $arg);
    $receiver = null; $callback = null; $arg = null;
    return $bytes . 'F;';
}
ob_start('exit_review_string_bound_final');
echo 'B;';
exit('E;');
