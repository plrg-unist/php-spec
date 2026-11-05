<?php
class TickArgOne { public function __destruct() { echo 'A1;'; } }
class TickArgTwo { public function __destruct() { echo 'A2;'; } }
class TickCaller {
    public function __invoke($first, $second) { echo 'BAD-CALL;'; }
    public function __destruct() { echo 'C;'; }
}
function shared_final($bytes, $phase) {
    $c = new TickCaller();
    register_tick_function($c);
    $a1 = new TickArgOne(); $a2 = new TickArgTwo();
    register_tick_function($c, $a1, $a2);
    $c = null; $a1 = null; $a2 = null;
    return $bytes . 'F;';
}
ob_start('shared_final');
echo 'B;';
