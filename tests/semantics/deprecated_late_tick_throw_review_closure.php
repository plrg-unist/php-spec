<?php
class ThrowTick19ClosureArg {
    public function __destruct() { echo 'A;'; throw new Exception('closure-arg-failure'); }
}
function throw_review_closure_final($bytes, $phase) {
    $tag = 'held';
    $callback = function (...$args) use ($tag) { echo 'BAD-CALL;'; };
    $throwing = new ThrowTick19ClosureArg();
    register_tick_function($callback, $throwing);
    $callback = null; $throwing = null; $tag = null;
    return $bytes . 'F;';
}
ob_start('throw_review_closure_final');
echo 'B;';
