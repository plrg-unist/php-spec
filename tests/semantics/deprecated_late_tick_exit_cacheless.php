<?php
function exit_tick18_named() { echo 'BAD-CALL;'; }
function exit_tick18_cacheless_final($bytes, $phase) {
    register_tick_function('exit_tick18_named');
    return $bytes . 'F;';
}
ob_start('exit_tick18_cacheless_final');
echo 'B;';
exit(263);
