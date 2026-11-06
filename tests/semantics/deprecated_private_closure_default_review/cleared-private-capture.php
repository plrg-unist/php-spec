<?php
#[Deprecated] const X = [];
class Scope190Capture {}
class Captured190 { public function __destruct() { echo 'D|'; } }
$held = new Captured190();
$original = function($value = X) use ($held) { echo 'E|'; return 7; };
$scoped = $original->bindTo(null, Scope190Capture::class);
$private = $scoped->bindTo(null, null);
$held = null;
$original = null;
$scoped = null;
set_error_handler(function() {
    global $private;
    echo 'H|';
    $private = null;
    return true;
});
$result = $private();
echo $result, '|';
