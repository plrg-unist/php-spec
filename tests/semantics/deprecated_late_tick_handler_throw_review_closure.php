<?php
class HandlerThrowClosure25Held { function __destruct() { echo 'K;'; } }
class HandlerThrowClosure25Returned {
    function __destruct() { echo 'R;'; throw new Exception('handler-closure-value-fail'); }
}
class HandlerThrowClosure25Later { function __destruct() { echo 'L;'; } }
class HandlerThrowClosure25Arg {
    public $held;
    function __construct() { $this->held = new HandlerThrowClosure25Held; }
    function __destruct() { echo 'A;'; throw new Exception('handler-closure-value'); }
}
class HandlerThrowClosure25Caller {
    function __invoke(...$args) { echo 'BAD-TICK-CALL;'; }
    function __destruct() { echo 'C;'; }
}
function handler_throw_closure25_handler($exception) {
    echo 'H;';
    $returned = new HandlerThrowClosure25Returned;
    return static function () use ($returned) { echo 'BAD-RETURN-CALL;'; };
}
class HandlerThrowClosure25Queue { function __destruct() { echo 'Q;'; } }
function handler_throw_closure25_never($argument) { echo 'BAD-QUEUE-CALL;'; }
function handler_throw_closure25_final($bytes, $phase) {
    $callback = new HandlerThrowClosure25Caller;
    $arg = new HandlerThrowClosure25Arg;
    $later = new HandlerThrowClosure25Later;
    register_tick_function($callback, $arg, $later);
    register_shutdown_function('handler_throw_closure25_never', new HandlerThrowClosure25Queue);
    unset($callback, $arg, $later);
    return $bytes . 'F;';
}
set_exception_handler('handler_throw_closure25_handler');
ob_start('handler_throw_closure25_final');
echo 'B;';
