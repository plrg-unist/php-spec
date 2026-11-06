<?php
namespace {
    const X = 9;
    class Scope190Invoke {}
}
namespace Ns190Invoke {
    $original = function($value = X, $tag = 0) { echo $value === 9 ? 'N|' : 'E|', $tag, '|'; };
    $scoped = $original->bindTo(null, \Scope190Invoke::class);
    $private = $scoped->bindTo(null, null);
    $private->__invoke(tag: 1);
    #[\Deprecated] const X = [];
    set_error_handler(function() { echo 'H|'; return true; });
    $original(tag: 2);
    $private(tag: 3);
}
