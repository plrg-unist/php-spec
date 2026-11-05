<?php
class ReferenceArrayTickArg { public function __destruct() { echo 'A;'; } }
class ReferenceArrayTickCaller {
    public function __invoke(...$args) { echo 'BAD-CALL;'; }
    public function __destruct() { echo 'C;'; }
}
function values_review_array_reference_final($bytes, $phase) {
    $c = new ReferenceArrayTickCaller();
    $r = 3; $alias =& $r; $payload = [&$alias];
    register_tick_function($c, $payload, $payload);
    $r = new ReferenceArrayTickArg();
    unset($payload, $alias, $r, $c);
    return $bytes . 'F;';
}
ob_start('values_review_array_reference_final');
echo 'B;';
