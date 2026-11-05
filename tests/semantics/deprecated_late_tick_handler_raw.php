<?php
class HandledTick21Arg {
    function __destruct() { echo 'A;'; throw new Exception('tick-handled'); }
}
class HandledTick21Later { function __destruct() { echo 'L;'; } }
class HandledTick21Caller {
    function __invoke(...$args) { echo 'BAD-CALL;'; }
    function __destruct() { echo 'C;'; }
}
function handled_tick21_exception($exception) { echo 'H;'; return null; }
function handled_tick21_final($bytes, $phase) {
    $callback = new HandledTick21Caller;
    $arg = new HandledTick21Arg;
    $later = new HandledTick21Later;
    register_tick_function($callback, $arg, $later);
    unset($callback, $arg, $later);
    return $bytes . 'F;';
}
set_exception_handler('handled_tick21_exception');
ob_start('handled_tick21_final');
echo 'B;';
