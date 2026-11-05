<?php
class BodyReexitRetained27Held { function __destruct() { echo 'K;'; } }
class BodyReexitRetained27Returned {
    function __destruct() { echo 'R;'; exit(9); }
}
class BodyReexitRetained27Tail { function __destruct() { echo 'U;'; } }
class BodyReexitRetained27Queue { function __destruct() { echo 'Q;'; } }
class BodyReexitRetained27Arg {
    public $held;
    public $returned;
    function __construct($held, $returned) {
        $this->held = $held;
        $this->returned = $returned;
    }
    function __destruct() { echo 'A;'; return $this->returned; }
}
class BodyReexitRetained27Caller {
    function __invoke(...$args) { echo 'BAD-TICK-CALL;'; }
    function __destruct() { echo 'C;'; }
}
function body_reexit_retained27_tail($argument) { echo 'BAD-TAIL-CALL;'; }
function body_reexit_retained27_queue($argument) { echo 'BAD-QUEUE-CALL;'; }
function body_reexit_retained27_final($bytes, $phase) {
    $callback = new BodyReexitRetained27Caller;
    $returned = new BodyReexitRetained27Returned;
    $arg = new BodyReexitRetained27Arg(new BodyReexitRetained27Held, $returned);
    $tail = new BodyReexitRetained27Tail;
    $queued = new BodyReexitRetained27Queue;
    register_tick_function($callback, $arg, $returned);
    register_tick_function('body_reexit_retained27_tail', $tail);
    register_shutdown_function('body_reexit_retained27_queue', $queued);
    unset($callback, $arg, $returned, $tail, $queued);
    return $bytes . 'F;';
}
ob_start('body_reexit_retained27_final');
echo 'B;';
exit(263);
