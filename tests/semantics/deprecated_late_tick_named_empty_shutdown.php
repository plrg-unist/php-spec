<?php
function named_empty_tick() { echo 'BAD-CALL;'; }
function named_empty_shutdown() { echo 'S;'; }
function named_empty_final($bytes, $phase) {
    register_tick_function('named_empty_tick');
    return $bytes . 'F;';
}
register_shutdown_function('named_empty_shutdown');
ob_start('named_empty_final');
echo 'B;';
