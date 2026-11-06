<?php
#[Deprecated] const X = [];
class Captured188 { public function __destruct() { echo 'D|'; } }
$held = new Captured188();
$original = function($value = X) use ($held) { echo 'E|'; return 7; };
$held = null;
set_error_handler(function() {
    global $original;
    echo 'H|';
    $original = null;
    return true;
});
$result = $original();
echo $result, '|';
