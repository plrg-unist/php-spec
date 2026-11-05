<?php
class ThrowShutdown19Arg {
    public function __destruct() { echo 'A;'; throw new Exception('shutdown-arg-failure'); }
}
class ThrowShutdown19QueueArg { public function __destruct() { echo 'Q;'; } }
class ThrowShutdown19Caller {
    public function __invoke(...$args) { echo 'BAD-CALL;'; }
    public function __destruct() { echo 'C;'; }
}
function throw_shutdown19_never($arg) { echo 'BAD-SHUTDOWN;'; }
function throw_review_shutdown_final($bytes, $phase) {
    $queue_arg = new ThrowShutdown19QueueArg();
    $callback = new ThrowShutdown19Caller(); $throwing = new ThrowShutdown19Arg();
    register_shutdown_function('throw_shutdown19_never', $queue_arg);
    register_tick_function($callback, $throwing);
    $queue_arg = null; $callback = null; $throwing = null;
    return $bytes . 'F;';
}
ob_start('throw_review_shutdown_final');
echo 'B;';
