<?php
#[Deprecated] const X = [];
class Scope190 {}
$original = function($value = X, $tag = 0) { $value[] = $tag; echo $value[0], '|'; };
$scoped = $original->bindTo(null, Scope190::class);
$private = $scoped->bindTo(null, null);
$scoped = null;
set_error_handler(function() { echo 'H|'; return true; });
$private(tag: 1);
$copy = clone $private;
$copy(tag: 2);
$private(tag: 3);
$rebound = $private->bindTo(null, null);
$rebound(tag: 4);
$original(tag: 5);
$private(tag: 6);
$original(tag: 7);
