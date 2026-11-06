<?php
#[Deprecated] const X = [];
class Scope188 {}
$original = function($value = X) { echo 'E|'; };
set_error_handler(function() {
    global $original;
    echo 'H|';
    $private = $original->bindTo(null, Scope188::class);
    $private = null;
    return true;
});
$original();
$original();
