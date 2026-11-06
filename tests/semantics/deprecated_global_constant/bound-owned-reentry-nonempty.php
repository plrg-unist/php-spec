<?php
namespace {
#[Deprecated] const X = [1];
function notice189($level, $message) {
    global $fn;
    echo 'H|';
    define('Ns189\\X', 9);
    $fn();
    return true;
}
}
namespace Ns189 {
$original = static function($value = X) { echo $value === 9 ? 'N|' : 'E|'; };
$fn = $original->bindTo(null, null); $original = null;
set_error_handler('notice189');
$fn(); $fn();
}
