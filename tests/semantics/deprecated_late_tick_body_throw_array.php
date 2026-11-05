<?php
class BodyArrayThrow23Value {
    public $owner;
    function __construct($owner) { $this->owner = $owner; }
    function __destruct() { echo 'R;'; throw new Exception('array-body-value'); }
}
class BodyArrayThrow23Child { function __destruct() { echo 'K;'; } }
class BodyArrayThrow23Arg {
    public $held;
    function __construct() { $this->held = new BodyArrayThrow23Child; }
    function __destruct() {
        echo 'A;';
        $returned = new BodyArrayThrow23Value($this);
        return [&$returned, $returned, $returned];
    }
}
class BodyArrayThrow23Later { function __destruct() { echo 'L;'; } }
class BodyArrayThrow23Caller {
    function __invoke(...$args) { echo 'BAD-CALL;'; }
    function __destruct() { echo 'C;'; }
}
class BodyArrayThrow23Queue { function __destruct() { echo 'Q;'; } }
function body_array_throw23_queue($arg) { echo 'BAD-QUEUE;'; }
function body_array_throw23_final($bytes, $phase) {
    $callback = new BodyArrayThrow23Caller;
    $arg = new BodyArrayThrow23Arg;
    $later = new BodyArrayThrow23Later;
    $queue = new BodyArrayThrow23Queue;
    register_tick_function($callback, $arg, $later);
    register_shutdown_function('body_array_throw23_queue', $queue);
    unset($callback, $arg, $later, $queue);
    return $bytes . 'F;';
}
ob_start('body_array_throw23_final');
echo 'B;';
exit(263);
