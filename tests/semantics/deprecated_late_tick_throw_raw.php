<?php
class ThrowTick19Arg {
    public function __destruct() { echo 'A;'; throw new Exception('tick-fail'); }
}
class ThrowTick19Caller {
    public function __invoke(...$args) { echo 'BAD-CALL;'; }
    public function __destruct() { echo 'C;'; }
}
function throw_tick19_final($bytes, $phase) {
    $callback = new ThrowTick19Caller(); $arg = new ThrowTick19Arg();
    register_tick_function($callback, $arg);
    $callback = null; $arg = null;
    return $bytes . 'F;';
}
ob_start('throw_tick19_final');
echo 'B;';
