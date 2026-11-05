<?php
class BodyExitRetained26Held { function __destruct() { echo 'K;'; } }
class BodyExitRetained26Returned {
    function __destruct() { echo 'R;'; exit(9); }
}
class BodyExitRetained26Tail { function __destruct() { echo 'U;'; } }
class BodyExitRetained26Queue { function __destruct() { echo 'Q;'; } }
class BodyExitRetained26Arg {
    public $held;
    public $returned;
    function __construct($held, $returned) {
        $this->held = $held;
        $this->returned = $returned;
    }
    function __destruct() { echo 'A;'; return $this->returned; }
}
class BodyExitRetained26Caller {
    function __invoke(...$args) { echo 'BAD-TICK-CALL;'; }
    function __destruct() { echo 'C;'; }
}
function body_exit_retained26_tail($argument) { echo 'BAD-TAIL-CALL;'; }
function body_exit_retained26_queue($argument) { echo 'BAD-QUEUE-CALL;'; }
function body_exit_retained26_final($bytes, $phase) {
    $callback = new BodyExitRetained26Caller;
    $returned = new BodyExitRetained26Returned;
    $arg = new BodyExitRetained26Arg(new BodyExitRetained26Held, $returned);
    $tail = new BodyExitRetained26Tail;
    $queued = new BodyExitRetained26Queue;
    register_tick_function($callback, $arg, $returned);
    register_tick_function('body_exit_retained26_tail', $tail);
    register_shutdown_function('body_exit_retained26_queue', $queued);
    unset($callback, $arg, $returned, $tail, $queued);
    return $bytes . 'F;';
}
ob_start('body_exit_retained26_final');
echo 'B;';
