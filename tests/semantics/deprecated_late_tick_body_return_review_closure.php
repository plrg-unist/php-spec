<?php
class BodyClosure22Held {
    function __destruct() { echo 'K;'; }
}
class BodyClosure22Returned {
    function __destruct() { echo 'R;'; }
}
class BodyClosure22Later {
    function __destruct() { echo 'L;'; }
}
class BodyClosure22Arg {
    public $held;
    function __construct($held) { $this->held = $held; }
    function __destruct() {
        echo 'A;';
        $returned = new BodyClosure22Returned;
        return static function () use ($returned) { echo 'BAD-RETURN-CALL;'; };
    }
}
class BodyClosure22Caller {
    function __invoke(...$args) { echo 'BAD-TICK-CALL;'; }
    function __destruct() { echo 'C;'; }
}
function body_closure22_final($bytes, $phase) {
    $callback = new BodyClosure22Caller;
    $arg = new BodyClosure22Arg(new BodyClosure22Held);
    $later = new BodyClosure22Later;
    register_tick_function($callback, $arg, $later);
    unset($callback, $arg, $later);
    return $bytes . 'F;';
}
ob_start('body_closure22_final');
echo 'B;';
