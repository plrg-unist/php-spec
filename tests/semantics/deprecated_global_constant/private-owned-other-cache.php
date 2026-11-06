<?php
namespace {
#[Deprecated] const X = [];
class Scope190 {}
function notice190() {
    global $other;
    echo 'H|'; define('Ns190\\X', 9); $other(); return true;
}
}
namespace Ns190 {
$original = function($value = X) { echo $value === 9 ? 'N|' : 'E|'; };
$scoped = $original->bindTo(null, \Scope190::class);
$fn = $scoped->bindTo(null, null); $other = clone $fn;
$original = $scoped = null;
set_error_handler('notice190');
$fn(); $fn(); $other();
}
