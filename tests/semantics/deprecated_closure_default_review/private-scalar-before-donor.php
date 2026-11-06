<?php
namespace {
    const X = 9;
    class Scope188 {}
}
namespace Ns188Review {
    function make188() {
        return function($value = X) { echo $value === 9 ? 'N|' : 'E|'; };
    }
    $original = make188();
    $private = $original->bindTo(null, \Scope188::class);
    $private();
    #[\Deprecated] const X = [];
    set_error_handler(function() { echo 'H|'; return true; });
    $original();
    $private();
}
