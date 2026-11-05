<?php
class BodyExit26Value { function __destruct() { echo 'R;'; exit(7); echo 'BAD-R;'; } }
class BodyExit26Child { function __destruct() { echo 'K;'; } }
class BodyExit26Arg {
    public $held;
    function __construct() { $this->held = new BodyExit26Child; }
    function __destruct() { echo 'A;'; return new BodyExit26Value; }
}
class BodyExit26Later { function __destruct() { echo 'L;'; } }
class BodyExit26Caller {
    function __invoke(...$args) { echo 'BAD-CALL;'; }
    function __destruct() { echo 'C;'; }
}
class BodyExit26TailArg { function __destruct() { echo 'U;'; } }
class BodyExit26Tail {
    function __invoke(...$args) { echo 'BAD-TAIL;'; }
    function __destruct() { echo 'T;'; }
}
class BodyExit26Queue { function __destruct() { echo 'Q;'; } }
function body_exit26_queue($arg) { echo 'BAD-QUEUE;'; }
function body_exit26_final($bytes, $phase) {
    $callback = new BodyExit26Caller;
    $arg = new BodyExit26Arg;
    $later = new BodyExit26Later;
    $tail = new BodyExit26Tail;
    $tailArg = new BodyExit26TailArg;
    $queue = new BodyExit26Queue;
    register_tick_function($callback, $arg, $later);
    register_tick_function($tail, $tailArg);
    register_shutdown_function('body_exit26_queue', $queue);
    unset($callback, $arg, $later, $tail, $tailArg, $queue);
    return $bytes . 'F;';
}
ob_start('body_exit26_final');
echo 'B;';
