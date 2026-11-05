<?php
function named_scalar_tick($arg) { echo 'BAD-CALL;'; }
function named_scalar_final($bytes, $phase) {
    register_tick_function('named_scalar_tick', null, 7, 's');
    return $bytes . 'F;';
}
ob_start('named_scalar_final');
echo 'B;';
