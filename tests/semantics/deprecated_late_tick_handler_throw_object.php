<?php
class HandlerThrow25Child { function __destruct() { echo 'K;'; } }
class HandlerThrow25Value {
    function __destruct() { echo 'R;'; throw new Exception('ignored-handler-value'); }
}
class HandlerThrow25Arg {
    public $child;
    function __construct() { $this->child = new HandlerThrow25Child; }
    function __destruct() { echo 'A;'; throw new Exception('handler-original'); }
}
class HandlerThrow25Later { function __destruct() { echo 'L;'; } }
class HandlerThrow25Tail { function __destruct() { echo 'U;'; } }
class HandlerThrow25Queued { function __destruct() { echo 'Q;'; } }
class HandlerThrow25Caller {
    function __invoke(...$arguments) { echo 'BAD-CALL;'; }
    function __destruct() { echo 'C;'; }
}
function handler_throw25_exception($exception) { echo 'H;'; return new HandlerThrow25Value; }
function handler_throw25_tail($argument) { echo 'BAD-TAIL;'; }
function handler_throw25_shutdown($argument) { echo 'BAD-SHUTDOWN;'; }
function handler_throw25_final($bytes, $phase) {
    $caller = new HandlerThrow25Caller;
    $argument = new HandlerThrow25Arg;
    $later = new HandlerThrow25Later;
    $tail = new HandlerThrow25Tail;
    $queued = new HandlerThrow25Queued;
    register_tick_function($caller, $argument, $later);
    register_tick_function('handler_throw25_tail', $tail);
    register_shutdown_function('handler_throw25_shutdown', $queued);
    unset($caller, $argument, $later, $tail, $queued);
    return $bytes . 'F;';
}
set_exception_handler('handler_throw25_exception');
ob_start('handler_throw25_final');
echo 'B;';
