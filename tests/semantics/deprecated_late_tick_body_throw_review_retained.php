<?php
class BodyRetained23Held { function __destruct() { echo 'K;'; } }
class BodyRetained23Returned {
    function __destruct() { echo 'R;'; throw new Exception('retained-body-value-fail'); }
}
class BodyRetained23Queue { function __destruct() { echo 'Q;'; } }
class BodyRetained23Arg {
    public $held;
    public $returned;
    function __construct($returned) {
        $this->held = new BodyRetained23Held;
        $this->returned = $returned;
    }
    function __destruct() { echo 'A;'; return $this->returned; }
}
class BodyRetained23Caller {
    function __invoke(...$args) { echo 'BAD-TICK-CALL;'; }
    function __destruct() { echo 'C;'; }
}
function body_retained23_never($arg) { echo 'BAD-QUEUE-CALL;'; }
function body_retained23_final($bytes, $phase) {
    $callback = new BodyRetained23Caller;
    $returned = new BodyRetained23Returned;
    $arg = new BodyRetained23Arg($returned);
    register_tick_function($callback, $arg, $returned);
    register_shutdown_function('body_retained23_never', new BodyRetained23Queue);
    unset($callback, $arg, $returned);
    return $bytes . 'F;';
}
ob_start('body_retained23_final');
echo 'B;';
