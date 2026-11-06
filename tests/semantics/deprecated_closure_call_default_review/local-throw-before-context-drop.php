<?php
#[Deprecated] const X = [];
class Receiver191 { public function __destruct() { echo 'R|'; } }
class Captured191 { public function __destruct() { echo 'C|'; } }
class Local191 {
    public function __destruct() { global $boom; echo 'L|'; throw $boom; }
}
$boom = new Exception('tail');
$held = new Captured191();
$fn = function($value = X) use ($held) {
    echo 'E|'; $local = new Local191(); return 7;
};
$held = null;
set_error_handler(function() {
    global $fn;
    echo 'H|'; $fn = null; return true;
});
$result = 1;
try { $result = $fn->call(new Receiver191()); }
catch (Exception $caught) { echo 'K|'; }
echo $result, '|';
