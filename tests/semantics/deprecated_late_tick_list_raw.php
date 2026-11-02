<?php
class TickArgOne { public function __destruct() { echo 'A1;'; } }
class TickArgTwo { public function __destruct() { echo 'A2;'; } }
class TickArgThree { public function __destruct() { echo 'A3;'; } }
class TickCallerOne {
    public function __invoke($arg) { echo 'BAD-CALL;'; }
    public function __destruct() { echo 'C1;'; }
}
class TickCallerTwo {
    public function __invoke($arg) { echo 'BAD-CALL;'; }
    public function __destruct() { echo 'C2;'; }
}
class TickCallerThree {
    public function __invoke($arg) { echo 'BAD-CALL;'; }
    public function __destruct() { echo 'C3;'; }
}
function three_final($bytes, $phase) {
    $c1 = new TickCallerOne(); $a1 = new TickArgOne();
    register_tick_function($c1, $a1);
    $c2 = new TickCallerTwo(); $a2 = new TickArgTwo();
    register_tick_function($c2, $a2);
    $c3 = new TickCallerThree(); $a3 = new TickArgThree();
    register_tick_function($c3, $a3);
    $c1 = null; $a1 = null; $c2 = null; $a2 = null; $c3 = null; $a3 = null;
    return $bytes . 'F;';
}
ob_start('three_final');
echo 'B;';
