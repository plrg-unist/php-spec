<?php
namespace {
#[Deprecated] const X = [];
function notice188($level, $message) {
    global $fn;
    echo 'H|';
    define('Ns188\\X', 9);
    $fn();
    return true;
}
}
namespace Ns188 {
$fn = static function($value = X) { echo $value === 9 ? 'N|' : 'E|'; };
set_error_handler('notice188');
$fn(); $fn();
}
