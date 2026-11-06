<?php
namespace {
#[Deprecated] const X = [];
class Scope190 {}
function notice190() {
    global $fn;
    echo 'H|'; define('Ns190\\X', 9); $fn(); return true;
}
}
namespace Ns190 {
$original = function($value = X) { echo $value === 9 ? 'N|' : 'E|'; };
$scoped = $original->bindTo(null, \Scope190::class);
$fn = $scoped->bindTo(null, null); $original = $scoped = null;
set_error_handler('notice190');
$fn(); $fn();
}
