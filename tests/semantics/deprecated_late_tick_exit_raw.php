<?php
class ExitTick18Arg { public function __destruct() { echo 'A;'; } }
class ExitTick18Caller {
    public function __invoke(...$args) { echo 'BAD-CALL;'; }
    public function __destruct() { echo 'C;'; }
}
function exit_tick18_final($bytes, $phase) {
    $callback = new ExitTick18Caller(); $arg = new ExitTick18Arg();
    register_tick_function($callback, $arg);
    $callback = null; $arg = null;
    return $bytes . 'F;';
}
ob_start('exit_tick18_final');
echo 'B;';
exit(7);
