<?php
class HandledCapture21Arg {
    function __destruct() { echo 'A;'; throw new Exception('exit-handled'); }
}
class HandledCapture21Child { function __destruct() { echo 'K;'; } }
function handled_capture21_exception($exception) { echo 'H;'; return null; }
function handled_capture21_final($bytes, $phase) {
    $child = new HandledCapture21Child;
    $callback = static function (...$args) use ($child) { echo 'BAD-CALL;'; };
    $arg = new HandledCapture21Arg;
    register_tick_function($callback, $arg);
    unset($child, $callback, $arg);
    return $bytes . 'F;';
}
set_exception_handler('handled_capture21_exception');
ob_start('handled_capture21_final');
echo 'B;';
exit(7);
