<?php
class HandlerValueRetained24State { public static $returned; }
class HandlerValueRetained24Held { function __destruct() { echo 'K;'; } }
class HandlerValueRetained24Returned { function __destruct() { echo 'R;'; } }
class HandlerValueRetained24Arg {
    public $held;
    function __construct() { $this->held = new HandlerValueRetained24Held; }
    function __destruct() { echo 'A;'; throw new Exception('handler-retained-value'); }
}
class HandlerValueRetained24Caller {
    function __invoke(...$args) { echo 'BAD-TICK-CALL;'; }
    function __destruct() { echo 'C;'; }
}
function handler_value_retained24_handler($exception) {
    echo 'H;';
    $returned = HandlerValueRetained24State::$returned;
    HandlerValueRetained24State::$returned = null;
    return $returned;
}
function handler_value_retained24_final($bytes, $phase) {
    $callback = new HandlerValueRetained24Caller;
    $returned = new HandlerValueRetained24Returned;
    $arg = new HandlerValueRetained24Arg;
    HandlerValueRetained24State::$returned = $returned;
    register_tick_function($callback, $arg, $returned);
    unset($callback, $arg, $returned);
    return $bytes . 'F;';
}
set_exception_handler('handler_value_retained24_handler');
ob_start('handler_value_retained24_final');
echo 'B;';
