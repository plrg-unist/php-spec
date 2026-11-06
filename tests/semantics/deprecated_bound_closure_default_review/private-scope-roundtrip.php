<?php
#[Deprecated] const X = [];
class Scope189 {}
$original = function($value = X) { echo 'E|'; };
$private = $original->bindTo(null, Scope189::class);
$roundtrip = $private->bindTo(null, null);
set_error_handler(function() { echo 'H|'; return true; });
$roundtrip();
