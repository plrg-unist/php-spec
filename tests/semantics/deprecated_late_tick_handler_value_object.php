<?php
class HandlerValue24Child { function __destruct() { echo 'K;'; } }
class HandlerValue24Result { function __destruct() { echo 'R;'; } }
class HandlerValue24Arg {
    public $child;
    function __construct() { $this->child = new HandlerValue24Child; }
    function __destruct() { echo 'A;'; throw new Exception('handler-owning-result'); }
}
class HandlerValue24Later { function __destruct() { echo 'L;'; } }
class HandlerValue24Caller {
    function __invoke(...$arguments) { echo 'BAD-CALL;'; }
    function __destruct() { echo 'C;'; }
}
function handler_value24_exception($exception) {
    echo 'H;';
    return new HandlerValue24Result;
}
function handler_value24_final($bytes, $phase) {
    $callback = new HandlerValue24Caller;
    $argument = new HandlerValue24Arg;
    $later = new HandlerValue24Later;
    register_tick_function($callback, $argument, $later);
    unset($callback, $argument, $later);
    return $bytes . 'F;';
}
set_exception_handler('handler_value24_exception');
ob_start('handler_value24_final');
echo 'B;';
