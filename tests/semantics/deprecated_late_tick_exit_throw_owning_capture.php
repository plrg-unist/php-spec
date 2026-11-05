<?php
class ExitThrowCapture20Arg {
    function __destruct() { echo 'A;'; throw new Exception('exit-capture-fail'); }
}
class ExitThrowCapture20Child { function __destruct() { echo 'K;'; } }
function exit_throw_capture20_final($bytes, $phase) {
    $child = new ExitThrowCapture20Child;
    $callback = static function (...$args) use ($child) { echo 'BAD-CALL;'; };
    $arg = new ExitThrowCapture20Arg;
    register_tick_function($callback, $arg);
    unset($child, $callback, $arg);
    return $bytes . 'F;';
}
ob_start('exit_throw_capture20_final');
echo 'B;';
exit(263);
