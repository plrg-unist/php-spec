<?php
class IntegerExitTickCapture { public function __destruct() { echo 'K;'; } }
class IntegerExitTickArg { public function __destruct() { echo 'A;'; } }
function exit_review_integer_closure_final($bytes, $phase) {
    $capture = new IntegerExitTickCapture(); $r = new IntegerExitTickArg();
    $payload = [&$r];
    $callback = function (...$args) use ($capture) { echo 'BAD-CALL;'; };
    register_tick_function($callback, $payload, $payload);
    unset($capture, $r, $payload, $callback);
    return $bytes . 'F;';
}
ob_start('exit_review_integer_closure_final');
echo 'B;';
exit(7);
