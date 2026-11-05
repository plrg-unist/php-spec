<?php
class SelfTickCaller {
    public function __invoke($arg) { echo 'BAD-CALL;'; }
    public function __destruct() { echo 'C;'; }
}
function self_final($bytes, $phase) {
    $c = new SelfTickCaller();
    register_tick_function($c, $c);
    $c = null;
    return $bytes . 'F;';
}
ob_start('self_final');
echo 'B;';
