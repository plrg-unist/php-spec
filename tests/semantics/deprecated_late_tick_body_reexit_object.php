<?php
class BodyReexit27Value { function __destruct() { echo 'R;'; exit(9); echo 'BAD-R;'; } }
class BodyReexit27Child { function __destruct() { echo 'K;'; } }
class BodyReexit27Arg {
    public $held;
    function __construct() { $this->held = new BodyReexit27Child; }
    function __destruct() { echo 'A;'; return new BodyReexit27Value; }
}
class BodyReexit27Later { function __destruct() { echo 'L;'; } }
class BodyReexit27Caller {
    function __invoke(...$args) { echo 'BAD-CALL;'; }
    function __destruct() { echo 'C;'; }
}
class BodyReexit27TailArg { function __destruct() { echo 'U;'; } }
class BodyReexit27Tail {
    function __invoke(...$args) { echo 'BAD-TAIL;'; }
    function __destruct() { echo 'T;'; }
}
class BodyReexit27Queue { function __destruct() { echo 'Q;'; } }
function body_reexit27_queue($arg) { echo 'BAD-QUEUE;'; }
function body_reexit27_final($bytes, $phase) {
    $callback = new BodyReexit27Caller;
    $arg = new BodyReexit27Arg;
    $later = new BodyReexit27Later;
    $tail = new BodyReexit27Tail;
    $tailArg = new BodyReexit27TailArg;
    $queue = new BodyReexit27Queue;
    register_tick_function($callback, $arg, $later);
    register_tick_function($tail, $tailArg);
    register_shutdown_function('body_reexit27_queue', $queue);
    unset($callback, $arg, $later, $tail, $tailArg, $queue);
    return $bytes . 'F;';
}
ob_start('body_reexit27_final');
echo 'B;';
exit(263);
