<?php
class ExitThrow20Arg {
    function __destruct() { echo 'A;'; throw new Exception('exit-tick-fail'); }
}
function exit_throw20_named(...$args) { echo 'BAD-CALL;'; }
function exit_throw20_final($bytes, $phase) {
    $arg = new ExitThrow20Arg;
    register_tick_function('exit_throw20_named', $arg);
    unset($arg);
    return $bytes . 'F;';
}
ob_start('exit_throw20_final');
echo 'B;';
exit(263);
