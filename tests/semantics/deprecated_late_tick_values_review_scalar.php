<?php
class ScalarTickCaller {
    public function __invoke(...$args) { echo 'BAD-CALL;'; }
    public function __destruct() { echo 'C;'; }
}
function values_review_scalar_final($bytes, $phase) {
    $c = new ScalarTickCaller();
    register_tick_function($c, null, false, true, 7, 1.5, 's');
    $c = null;
    return $bytes . 'F;';
}
ob_start('values_review_scalar_final');
echo 'B;';
