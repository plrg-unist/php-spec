<?php
#[Deprecated] const X = [];
class Captured189 { public function __destruct() { echo 'D|'; } }
$held = new Captured189();
$original = function($value = X) use ($held) { echo 'E|'; return 7; };
$bound = Closure::bind($original, null, null);
$held = null;
$original = null;
set_error_handler(function() {
    global $bound;
    echo 'H|';
    $bound = null;
    return true;
});
$result = $bound();
echo $result, '|';
