<?php
class SharedArrayTickArg { public function __destruct() { echo 'A;'; } }
class SharedArrayTickOne {
    public function __invoke(...$args) { echo 'BAD-CALL;'; }
    public function __destruct() { echo 'C1;'; }
}
class SharedArrayTickTwo {
    public function __invoke(...$args) { echo 'BAD-CALL;'; }
    public function __destruct() { echo 'C2;'; }
}
function values_review_shared_array_final($bytes, $phase) {
    $c1 = new SharedArrayTickOne(); $c2 = new SharedArrayTickTwo();
    $a = new SharedArrayTickArg(); $payload = [[$a]];
    register_tick_function($c1, $payload, $payload);
    register_tick_function($c2, $payload);
    $c1 = null; $c2 = null; $a = null; $payload = null;
    return $bytes . 'F;';
}
ob_start('values_review_shared_array_final');
echo 'B;';
