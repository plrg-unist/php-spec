<?php
class BodyExitClosure26Held { function __destruct() { echo 'K;'; } }
class BodyExitClosure26Returned {
    function __destruct() { echo 'R;'; exit(263); }
}
class BodyExitClosure26Later { function __destruct() { echo 'L;'; } }
class BodyExitClosure26Tail { function __destruct() { echo 'U;'; } }
class BodyExitClosure26Queue { function __destruct() { echo 'Q;'; } }
class BodyExitClosure26Arg {
    public $held;
    function __construct($held) { $this->held = $held; }
    function __destruct() {
        echo 'A;';
        $returned = new BodyExitClosure26Returned;
        return static function () use ($returned) { echo 'BAD-RETURN-CALL;'; };
    }
}
class BodyExitClosure26Caller {
    function __invoke(...$args) { echo 'BAD-TICK-CALL;'; }
    function __destruct() { echo 'C;'; }
}
function body_exit_closure26_tail($argument) { echo 'BAD-TAIL-CALL;'; }
function body_exit_closure26_queue($argument) { echo 'BAD-QUEUE-CALL;'; }
function body_exit_closure26_final($bytes, $phase) {
    $callback = new BodyExitClosure26Caller;
    $arg = new BodyExitClosure26Arg(new BodyExitClosure26Held);
    $later = new BodyExitClosure26Later;
    $tail = new BodyExitClosure26Tail;
    $queued = new BodyExitClosure26Queue;
    register_tick_function($callback, $arg, $later);
    register_tick_function('body_exit_closure26_tail', $tail);
    register_shutdown_function('body_exit_closure26_queue', $queued);
    unset($callback, $arg, $later, $tail, $queued);
    return $bytes . 'F;';
}
ob_start('body_exit_closure26_final');
echo 'B;';
