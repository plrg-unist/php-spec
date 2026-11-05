<?php
class HandlerArrayThrow25State { public static $argument; }
class HandlerArrayThrow25Child { function __destruct() { echo 'K;'; } }
class HandlerArrayThrow25Value {
    public $owner;
    function __construct($owner) { $this->owner = $owner; }
    function __destruct() { echo 'R;'; throw new Exception('array-handler-value'); }
}
class HandlerArrayThrow25Arg {
    public $child;
    function __construct() { $this->child = new HandlerArrayThrow25Child; }
    function __destruct() {
        echo 'A;';
        HandlerArrayThrow25State::$argument = $this;
        throw new Exception('array-handler-original');
    }
}
class HandlerArrayThrow25Later { function __destruct() { echo 'L;'; } }
class HandlerArrayThrow25Queued { function __destruct() { echo 'Q;'; } }
class HandlerArrayThrow25Caller {
    function __invoke(...$arguments) { echo 'BAD-CALL;'; }
    function __destruct() { echo 'C;'; }
}
function handler_array_throw25_exception($exception) {
    echo 'H;';
    $argument = HandlerArrayThrow25State::$argument;
    HandlerArrayThrow25State::$argument = null;
    $returned = new HandlerArrayThrow25Value($argument);
    return [&$returned, $returned, $returned];
}
function handler_array_throw25_shutdown($argument) { echo 'BAD-SHUTDOWN;'; }
function handler_array_throw25_final($bytes, $phase) {
    $caller = new HandlerArrayThrow25Caller;
    $argument = new HandlerArrayThrow25Arg;
    $later = new HandlerArrayThrow25Later;
    $queued = new HandlerArrayThrow25Queued;
    register_tick_function($caller, $argument, $later);
    register_shutdown_function('handler_array_throw25_shutdown', $queued);
    unset($caller, $argument, $later, $queued);
    return $bytes . 'F;';
}
set_exception_handler('handler_array_throw25_exception');
ob_start('handler_array_throw25_final');
echo 'B;';
exit(263);
