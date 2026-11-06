<?php
#[Deprecated] const X = [];
class Receiver191 { public function __destruct() { echo 'R|'; } }
class Captured191 { public function __destruct() { echo 'C|'; } }
$held = new Captured191();
$fn = function($value = X) use ($held) { echo 'E|'; return 7; };
$held = null;
set_error_handler(function() {
    global $fn;
    echo 'H|'; $fn = null; return true;
});
$result = $fn->call(new Receiver191());
echo $result, '|';
