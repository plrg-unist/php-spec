<?php
class TickArgTwo { public function __destruct() { echo 'A2;'; } }
class TickCallerOne {
    public function __invoke() { echo 'BAD-CALL1;'; }
    public function __destruct() { echo 'C1;'; }
}
class TickCallerTwo {
    public function __invoke($arg) { echo 'BAD-CALL2;'; }
    public function __destruct() { echo 'C2;'; }
}
function mixed_final($bytes, $phase) {
    $c1 = new TickCallerOne();
    register_tick_function($c1);
    $c2 = new TickCallerTwo(); $a2 = new TickArgTwo();
    register_tick_function($c2, $a2);
    $c1 = null; $c2 = null; $a2 = null;
    return $bytes . 'F;';
}
ob_start('mixed_final');
echo 'B;';
