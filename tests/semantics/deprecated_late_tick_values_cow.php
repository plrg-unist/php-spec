<?php
class CowTickArg { public function __destruct() { echo 'A;'; } }
class CowTickCaller {
    public function __invoke(...$args) { echo 'BAD-CALL;'; }
    public function __destruct() { echo 'C;'; }
}
function values_cow_final($bytes, $phase) {
    $c = new CowTickCaller(); $a = new CowTickArg();
    $payload = [$a];
    register_tick_function($c, $payload);
    $payload[0] = null;
    $c = null; $a = null; $payload = null;
    return $bytes . 'F;';
}
ob_start('values_cow_final');
echo 'B;';
