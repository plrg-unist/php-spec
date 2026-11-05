<?php
class ThrowCapture19Arg {
    public function __destruct() { echo 'A;'; throw new Exception('tick-fail'); }
}
class ThrowCapture19Child { public function __destruct() { echo 'K;'; } }
function throw_capture19_final($bytes, $phase) {
    $keep = new ThrowCapture19Child(); $arg = new ThrowCapture19Arg();
    $callback = function (...$args) use ($keep) { echo 'BAD-CALL;'; };
    register_tick_function($callback, $arg);
    $callback = null; $arg = null; $keep = null;
    return $bytes . 'F;';
}
ob_start('throw_capture19_final');
echo 'B;';
