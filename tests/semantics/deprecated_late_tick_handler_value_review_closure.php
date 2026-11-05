<?php
class HandlerValueClosure24Held { function __destruct() { echo 'K;'; } }
class HandlerValueClosure24Returned { function __destruct() { echo 'R;'; } }
class HandlerValueClosure24Later { function __destruct() { echo 'L;'; } }
class HandlerValueClosure24Arg {
    public $held;
    function __construct() { $this->held = new HandlerValueClosure24Held; }
    function __destruct() { echo 'A;'; throw new Exception('handler-closure-value'); }
}
class HandlerValueClosure24Caller {
    function __invoke(...$args) { echo 'BAD-TICK-CALL;'; }
    function __destruct() { echo 'C;'; }
}
function handler_value_closure24_handler($exception) {
    echo 'H;';
    $returned = new HandlerValueClosure24Returned;
    return static function () use ($returned) { echo 'BAD-RETURN-CALL;'; };
}
function handler_value_closure24_final($bytes, $phase) {
    $callback = new HandlerValueClosure24Caller;
    $arg = new HandlerValueClosure24Arg;
    $later = new HandlerValueClosure24Later;
    register_tick_function($callback, $arg, $later);
    unset($callback, $arg, $later);
    return $bytes . 'F;';
}
set_exception_handler('handler_value_closure24_handler');
ob_start('handler_value_closure24_final');
echo 'B;';
