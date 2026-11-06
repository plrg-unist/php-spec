<?php
#[Deprecated] const X = [];
class Receiver193 {
    public function run($v = X) { echo $v === [] ? "E|" : "N|"; }
}
set_error_handler(function () { echo "H|"; return true; });
$receiver = new Receiver193;
$fn = $receiver->run(...);
$fn();
$fn->__invoke();
