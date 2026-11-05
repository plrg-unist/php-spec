<?php
class HandlerArray24State { public static $argument; }
class HandlerArray24Child { function __destruct() { echo 'K;'; } }
class HandlerArray24Result {
    public $owner;
    function __construct($owner) { $this->owner = $owner; }
    function __destruct() { echo 'R;'; }
}
class HandlerArray24Arg {
    public $child;
    function __construct() { $this->child = new HandlerArray24Child; }
    function __destruct() {
        echo 'A;';
        HandlerArray24State::$argument = $this;
        throw new Exception('handler-array-result');
    }
}
class HandlerArray24Later { function __destruct() { echo 'L;'; } }
class HandlerArray24Caller {
    function __invoke(...$arguments) { echo 'BAD-CALL;'; }
    function __destruct() { echo 'C;'; }
}
function handler_array24_exception($exception) {
    echo 'H;';
    $argument = HandlerArray24State::$argument;
    HandlerArray24State::$argument = null;
    $returned = new HandlerArray24Result($argument);
    return [&$returned, $returned, $returned];
}
function handler_array24_final($bytes, $phase) {
    $callback = new HandlerArray24Caller;
    $argument = new HandlerArray24Arg;
    $later = new HandlerArray24Later;
    register_tick_function($callback, $argument, $later);
    unset($callback, $argument, $later);
    return $bytes . 'F;';
}
set_exception_handler('handler_array24_exception');
ob_start('handler_array24_final');
echo 'B;';
exit(263);
