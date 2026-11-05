<?php
class BodyRetained22Held {
    function __destruct() { echo 'K;'; }
}
class BodyRetained22Returned {
    function __destruct() { echo 'R;'; }
}
class BodyRetained22Arg {
    public $held;
    public $returned;
    function __construct($held, $returned) {
        $this->held = $held;
        $this->returned = $returned;
    }
    function __destruct() { echo 'A;'; return $this->returned; }
}
class BodyRetained22Caller {
    function __invoke(...$args) { echo 'BAD-TICK-CALL;'; }
    function __destruct() { echo 'C;'; }
}
function body_retained22_final($bytes, $phase) {
    $callback = new BodyRetained22Caller;
    $returned = new BodyRetained22Returned;
    $arg = new BodyRetained22Arg(new BodyRetained22Held, $returned);
    register_tick_function($callback, $arg, $returned);
    unset($callback, $arg, $returned);
    return $bytes . 'F;';
}
ob_start('body_retained22_final');
echo 'B;';
