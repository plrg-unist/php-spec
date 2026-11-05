<?php
class BodyEmptyExit26Value {
    function __destruct() { echo 'R;'; exit(263); }
}
class BodyEmptyExit26Arg {
    function __destruct() { echo 'A;'; return new BodyEmptyExit26Value; }
}
function body_empty_exit26_tick($argument) { echo 'BAD-TICK;'; }
function body_empty_exit26_final($bytes, $phase) {
    $arg = new BodyEmptyExit26Arg;
    register_tick_function('body_empty_exit26_tick', $arg);
    unset($arg);
    return $bytes . 'F;';
}
ob_start('body_empty_exit26_final');
echo 'B;';
