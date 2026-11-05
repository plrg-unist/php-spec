<?php
class BodyReturn22Child { function __destruct() { echo 'K;'; } }
class BodyReturn22Value { function __destruct() { echo 'R;'; } }
class BodyReturn22Arg {
    public $held;
    function __construct() { $this->held = new BodyReturn22Child; }
    function __destruct() { echo 'A;'; return new BodyReturn22Value; }
}
class BodyReturn22Later { function __destruct() { echo 'L;'; } }
class BodyReturn22Caller {
    function __invoke(...$args) { echo 'BAD-CALL;'; }
    function __destruct() { echo 'C;'; }
}
function body_return22_final($bytes, $phase) {
    $callback = new BodyReturn22Caller;
    $arg = new BodyReturn22Arg;
    $later = new BodyReturn22Later;
    register_tick_function($callback, $arg, $later);
    unset($callback, $arg, $later);
    return $bytes . 'F;';
}
ob_start('body_return22_final');
echo 'B;';
