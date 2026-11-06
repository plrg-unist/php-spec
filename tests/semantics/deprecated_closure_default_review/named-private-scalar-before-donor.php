<?php
namespace {
    const X = 9;
    class NamedScope188 {}
}
namespace Ns188NamedReview {
    function make188() {
        return function($value = X, $last = 0) { echo $value === 9 ? 'N|' : 'E|', $last, '|'; };
    }
    $original = make188();
    $private = $original->bindTo(null, \NamedScope188::class);
    $private(last: 1);
    #[\Deprecated] const X = [];
    set_error_handler(function() { echo 'H|'; return true; });
    $original(last: 2);
    $private(last: 3);
}
