<?php
class HandlerThrowRetained25State { public static $returned; }
class HandlerThrowRetained25Held { function __destruct() { echo 'K;'; } }
class HandlerThrowRetained25Returned {
    function __destruct() { echo 'R;'; throw new Exception('handler-retained-value-fail'); }
}
class HandlerThrowRetained25Arg {
    public $held;
    function __construct() { $this->held = new HandlerThrowRetained25Held; }
    function __destruct() { echo 'A;'; throw new Exception('handler-retained-value'); }
}
class HandlerThrowRetained25Caller {
    function __invoke(...$args) { echo 'BAD-TICK-CALL;'; }
    function __destruct() { echo 'C;'; }
}
function handler_throw_retained25_handler($exception) {
    echo 'H;';
    $returned = HandlerThrowRetained25State::$returned;
    HandlerThrowRetained25State::$returned = null;
    return $returned;
}
class HandlerThrowRetained25Queue { function __destruct() { echo 'Q;'; } }
function handler_throw_retained25_never($argument) { echo 'BAD-QUEUE-CALL;'; }
function handler_throw_retained25_final($bytes, $phase) {
    $callback = new HandlerThrowRetained25Caller;
    $returned = new HandlerThrowRetained25Returned;
    $arg = new HandlerThrowRetained25Arg;
    HandlerThrowRetained25State::$returned = $returned;
    register_tick_function($callback, $arg, $returned);
    register_shutdown_function('handler_throw_retained25_never', new HandlerThrowRetained25Queue);
    unset($callback, $arg, $returned);
    return $bytes . 'F;';
}
set_exception_handler('handler_throw_retained25_handler');
ob_start('handler_throw_retained25_final');
echo 'B;';
