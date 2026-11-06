<?php
#[Deprecated] const X = [];
$original = function($value = X, $tag = 0) { echo 'E', $tag, '|'; };
set_error_handler(function() { echo 'H|'; return true; });
$cold = $original->bindTo(null, null);
$cold(tag: 1);
$omitted = $original->bindTo(null); $omitted();
$static = $original->bindTo(null, 'static'); $static();
$api = Closure::bind($original, null); $api();
$explicit = Closure::bind($original, null, null); $explicit();
$original();
