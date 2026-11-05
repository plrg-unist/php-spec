<?php
class BodyReexitClosure27Held { function __destruct() { echo 'K;'; } }
class BodyReexitClosure27Returned {
    function __destruct() { echo 'R;'; exit(519); }
}
class BodyReexitClosure27Later { function __destruct() { echo 'L;'; } }
class BodyReexitClosure27Tail { function __destruct() { echo 'U;'; } }
class BodyReexitClosure27Queue { function __destruct() { echo 'Q;'; } }
class BodyReexitClosure27Arg {
    public $held;
    function __construct($held) { $this->held = $held; }
    function __destruct() {
        echo 'A;';
        $returned = new BodyReexitClosure27Returned;
        return static function () use ($returned) { echo 'BAD-RETURN-CALL;'; };
    }
}
class BodyReexitClosure27Caller {
    function __invoke(...$args) { echo 'BAD-TICK-CALL;'; }
    function __destruct() { echo 'C;'; }
}
function body_reexit_closure27_tail($argument) { echo 'BAD-TAIL-CALL;'; }
function body_reexit_closure27_queue($argument) { echo 'BAD-QUEUE-CALL;'; }
function body_reexit_closure27_final($bytes, $phase) {
    $callback = new BodyReexitClosure27Caller;
    $arg = new BodyReexitClosure27Arg(new BodyReexitClosure27Held);
    $later = new BodyReexitClosure27Later;
    $tail = new BodyReexitClosure27Tail;
    $queued = new BodyReexitClosure27Queue;
    register_tick_function($callback, $arg, $later);
    register_tick_function('body_reexit_closure27_tail', $tail);
    register_shutdown_function('body_reexit_closure27_queue', $queued);
    unset($callback, $arg, $later, $tail, $queued);
    return $bytes . 'F;';
}
ob_start('body_reexit_closure27_final');
echo 'B;';
exit(263);
