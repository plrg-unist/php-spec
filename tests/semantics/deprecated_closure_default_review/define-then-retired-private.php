<?php
namespace {
    #[Deprecated] const X = [];
    class DefineScope188 {}
    function notice188() {
        global $original;
        echo 'H|';
        define('Ns188DefineReview\\Y', 9);
        $private = $original->bindTo(null, DefineScope188::class);
        $private = null;
        return true;
    }
}
namespace Ns188DefineReview {
    $original = function($value = X) { echo 'E|'; };
    set_error_handler('notice188');
    $original();
}
