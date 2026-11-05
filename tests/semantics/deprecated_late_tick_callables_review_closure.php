<?php
class ClosureTick17Capture { public function __destruct() { echo 'K;'; } }
class ClosureTick17Arg { public function __destruct() { echo 'A;'; } }
function callables_review_closure_final($bytes, $phase) {
    $capture = new ClosureTick17Capture(); $arg = new ClosureTick17Arg();
    $callback = function (...$args) use ($capture) { echo 'BAD-CALL;'; };
    register_tick_function($callback, $arg);
    $callback = null; $capture = null; $arg = null;
    return $bytes . 'F;';
}
ob_start('callables_review_closure_final');
echo 'B;';
