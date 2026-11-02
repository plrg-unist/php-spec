<?php
class LateTickArg {
    public function __destruct() { echo 'A;'; }
}
class LateTickCaller {
    public function __invoke($arg) { echo 'BAD-CALL;'; }
    public function __destruct() { echo 'C;'; }
}
function finish_buffer($bytes, $phase) {
    $callback = new LateTickCaller();
    $arg = new LateTickArg();
    register_tick_function($callback, $arg);
    $callback = null;
    $arg = null;
    return $bytes . 'F;';
}
function before_shutdown() { echo 'S;'; }
register_shutdown_function('before_shutdown');
ob_start('finish_buffer');
echo 'B;';
