<?php
class MixedTick17Arg { public function __destruct() { echo 'A;'; } }
class MixedTick17Method {
    public function run(...$args) { echo 'BAD-CALL;'; }
    public function __destruct() { echo 'M;'; }
}
function callables_review_named_tick17(...$args) { echo 'BAD-CALL;'; }
function callables_review_mixed_final($bytes, $phase) {
    $method = new MixedTick17Method(); $arg = new MixedTick17Arg();
    $payload = [$arg, $method];
    register_tick_function('callables_review_named_tick17', $payload);
    register_tick_function([$method, 'run'], $payload);
    $method = null; $arg = null; $payload = null;
    return $bytes . 'F;';
}
ob_start('callables_review_mixed_final');
echo 'B;';
