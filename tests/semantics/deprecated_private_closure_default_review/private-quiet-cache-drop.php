<?php
#[Deprecated] const X = [];
class Scope190Quiet {}
$original = function($value = X) { echo 'E|'; };
$scoped = $original->bindTo(null, Scope190Quiet::class);
$private = $scoped->bindTo(null, null);
$original = null;
$scoped = null;
set_error_handler(function() { echo 'H|'; return true; });
$private();
$private = null;
echo 'A|';
