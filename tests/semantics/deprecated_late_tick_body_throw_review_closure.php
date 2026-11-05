<?php
class BodyClosure23Held { function __destruct() { echo 'K;'; } }
class BodyClosure23Returned {
    function __destruct() { echo 'R;'; throw new Exception('closure-body-value-fail'); }
}
class BodyClosure23Later { function __destruct() { echo 'L;'; } }
class BodyClosure23Queue { function __destruct() { echo 'Q;'; } }
class BodyClosure23Arg {
    public $held;
    function __construct() { $this->held = new BodyClosure23Held; }
    function __destruct() {
        echo 'A;';
        $returned = new BodyClosure23Returned;
        return static function () use ($returned) { echo 'BAD-RETURN-CALL;'; };
    }
}
class BodyClosure23Caller {
    function __invoke(...$args) { echo 'BAD-TICK-CALL;'; }
    function __destruct() { echo 'C;'; }
}
function body_closure23_never($arg) { echo 'BAD-QUEUE-CALL;'; }
function body_closure23_final($bytes, $phase) {
    $callback = new BodyClosure23Caller;
    $arg = new BodyClosure23Arg;
    $later = new BodyClosure23Later;
    register_tick_function($callback, $arg, $later);
    register_shutdown_function('body_closure23_never', new BodyClosure23Queue);
    unset($callback, $arg, $later);
    return $bytes . 'F;';
}
ob_start('body_closure23_final');
echo 'B;';
