<?php
class HandlerTick21First {
    public function __destruct() { echo 'A;'; throw new Exception('handler-exit-tick'); }
}
class HandlerTick21Later { public function __destruct() { echo 'L;'; } }
class HandlerTick21TailArg { public function __destruct() { echo 'U;'; } }
class HandlerTick21QueueArg { public function __destruct() { echo 'Q;'; } }
class HandlerTick21Caller {
    public function __invoke(...$args) { echo 'BAD-CALL;'; }
    public function __destruct() { echo 'C;'; }
}
class HandlerTick21TailCaller {
    public function __invoke(...$args) { echo 'BAD-CALL;'; }
    public function __destruct() { echo 'T;'; }
}
function handler_tick21_never($arg) { echo 'BAD-SHUTDOWN;'; }
function handler_tick21_scalar($error) { echo 'H;'; return 23; }
function handler_review_tail_final($bytes, $phase) {
    $queue_arg = new HandlerTick21QueueArg();
    $callback = new HandlerTick21Caller(); $throwing = new HandlerTick21First();
    $later = new HandlerTick21Later(); $tail = new HandlerTick21TailCaller();
    $tail_arg = new HandlerTick21TailArg();
    register_shutdown_function('handler_tick21_never', $queue_arg);
    register_tick_function($callback, $throwing, $later);
    register_tick_function($tail, $tail_arg);
    $queue_arg = null; $callback = null; $throwing = null; $later = null;
    $tail = null; $tail_arg = null;
    return $bytes . 'F;';
}
set_exception_handler('handler_tick21_scalar');
ob_start('handler_review_tail_final');
echo 'B;';
exit(263);
