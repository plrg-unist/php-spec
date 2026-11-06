<?php
namespace {
    const X = 9;
    class Scope188 {}
}
namespace Ns188Review {
    $original = function($value = X) { echo $value === 9 ? 'N|' : 'E|'; };
    $receiver = new \Scope188();
    $original->call($receiver);
    #[\Deprecated] const X = [];
    set_error_handler(function() { echo 'H|'; return true; });
    $original();
}
