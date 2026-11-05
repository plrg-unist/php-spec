<?php
class OtherTickArg { public function __destruct() { echo 'A;'; } }
class SelfTickCaller {
    public function __invoke($first, $second) { echo 'BAD-CALL;'; }
    public function __destruct() { echo 'C;'; }
}
function self_other_final($bytes, $phase) {
    $c = new SelfTickCaller(); $a = new OtherTickArg();
    register_tick_function($c, $c, $a);
    $c = null; $a = null;
    return $bytes . 'F;';
}
ob_start('self_other_final');
echo 'B;';
