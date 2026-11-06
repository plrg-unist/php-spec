<?php
namespace {
#[Deprecated] const X = [1];
function notice193() { global $fn; echo 'H|'; define('Ns193\\X', 9); $fn(); return true; }
}
namespace Ns193 {
class Receiver193 { function read($value = X) { echo $value === 9 ? 'N|' : 'E|'; } }
$receiver = new Receiver193(); $fn = \Closure::fromCallable([$receiver, 'read']); $receiver = null;
set_error_handler('notice193'); $fn(); $fn();
}
