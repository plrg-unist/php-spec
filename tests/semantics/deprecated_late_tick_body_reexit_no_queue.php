<?php
class BodyEmptyReexit27Value {
    function __destruct() { echo 'R;'; exit(519); }
}
class BodyEmptyReexit27Arg {
    function __destruct() { echo 'A;'; return new BodyEmptyReexit27Value; }
}
function body_empty_reexit27_tick($argument) { echo 'BAD-TICK;'; }
function body_empty_reexit27_final($bytes, $phase) {
    $arg = new BodyEmptyReexit27Arg;
    register_tick_function('body_empty_reexit27_tick', $arg);
    unset($arg);
    return $bytes . 'F;';
}
ob_start('body_empty_reexit27_final');
echo 'B;';
exit(263);
