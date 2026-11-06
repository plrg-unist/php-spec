<?php
#[Deprecated] const X = [];
class Receiver191 { public function __destruct() { echo 'R|'; } }
class Captured191 { public function __destruct() { echo 'C|'; } }
class Local191 {
    public function __destruct() {
        global $fn, $receiver;
        echo 'L|';
        $fn->call(newThis: $receiver, inner: true);
        $fn = $receiver = null;
    }
}
$held = new Captured191(); $receiver = new Receiver191();
$fn = function($value = X, $inner = false) use ($held) {
    echo $inner ? 'I|' : 'E|';
    if (!$inner) { $local = new Local191(); }
    return 7;
};
$held = null;
set_error_handler(function() { echo 'H|'; return true; });
$result = $fn->call($receiver);
echo $result, '|';
