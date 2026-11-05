<?php
class BodyThrow23Value { function __destruct() { echo 'R;'; throw new Exception('body-value'); } }
class BodyThrow23Child { function __destruct() { echo 'K;'; } }
class BodyThrow23Arg {
    public $held;
    function __construct() { $this->held = new BodyThrow23Child; }
    function __destruct() { echo 'A;'; return new BodyThrow23Value; }
}
class BodyThrow23Later { function __destruct() { echo 'L;'; } }
class BodyThrow23Caller {
    function __invoke(...$args) { echo 'BAD-CALL;'; }
    function __destruct() { echo 'C;'; }
}
class BodyThrow23TailArg { function __destruct() { echo 'U;'; } }
class BodyThrow23Tail {
    function __invoke(...$args) { echo 'BAD-TAIL;'; }
    function __destruct() { echo 'T;'; }
}
class BodyThrow23Queue { function __destruct() { echo 'Q;'; } }
function body_throw23_queue($arg) { echo 'BAD-QUEUE;'; }
function body_throw23_final($bytes, $phase) {
    $callback = new BodyThrow23Caller;
    $arg = new BodyThrow23Arg;
    $later = new BodyThrow23Later;
    $tail = new BodyThrow23Tail;
    $tailArg = new BodyThrow23TailArg;
    $queue = new BodyThrow23Queue;
    register_tick_function($callback, $arg, $later);
    register_tick_function($tail, $tailArg);
    register_shutdown_function('body_throw23_queue', $queue);
    unset($callback, $arg, $later, $tail, $tailArg, $queue);
    return $bytes . 'F;';
}
ob_start('body_throw23_final');
echo 'B;';
