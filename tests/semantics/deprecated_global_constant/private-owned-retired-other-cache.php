<?php
namespace {
#[Deprecated] const X = [];
class Scope190 {}
function notice190() {
    global $other;
    echo 'H|'; define('Ns190\\X', 9); $other(); $other = null; return true;
}
}
namespace Ns190 {
$shared = function($value = X) { echo $value === 9 ? 'N|' : 'E|'; };
$scoped = $shared->bindTo(null, \Scope190::class);
$fn = $scoped->bindTo(null, null); $other = clone $fn; $scoped = null;
set_error_handler('notice190');
$fn(); $fn(); $shared();
}
