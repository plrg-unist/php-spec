<?php
class NestedSelfTickArg { public function __destruct() { echo 'A;'; } }
class NestedSelfTickCaller {
    public function __invoke(...$args) { echo 'BAD-CALL;'; }
    public function __destruct() { echo 'C;'; }
}
function values_review_nested_self_final($bytes, $phase) {
    $c = new NestedSelfTickCaller(); $a = new NestedSelfTickArg();
    $payload = [[$c], $a];
    register_tick_function($c, $payload);
    $c = null; $a = null; $payload = null;
    return $bytes . 'F;';
}
ob_start('values_review_nested_self_final');
echo 'B;';
