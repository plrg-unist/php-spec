<?php
namespace {
#[Deprecated] const X = [];
class Receiver192 { public int $tag = 7; }
function notice192() {
    global $fn;
    echo 'H|'; define('Ns192\\X', 9); $fn(); return true;
}
}
namespace Ns192 {
$original = function($value = X) { echo $value === 9 ? 'N|' : 'E|', $this->tag, '|'; };
$fn = $original->bindTo(new \Receiver192(), \Receiver192::class); $original = null;
set_error_handler('notice192'); $fn(); $fn();
}
