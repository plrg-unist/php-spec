<?php
class BodyArrayReexit27Child { function __destruct() { echo 'K;'; } }
class BodyArrayReexit27Value {
    public $owner;
    function __construct($owner) { $this->owner = $owner; }
    function __destruct() { echo 'R;'; exit(515); echo 'BAD-R;'; }
}
class BodyArrayReexit27Arg {
    public $held;
    function __construct() { $this->held = new BodyArrayReexit27Child; }
    function __destruct() {
        echo 'A;';
        $returned = new BodyArrayReexit27Value($this);
        return [&$returned, $returned, $returned];
    }
}
class BodyArrayReexit27Later { function __destruct() { echo 'L;'; } }
class BodyArrayReexit27Caller {
    function __invoke(...$args) { echo 'BAD-CALL;'; }
    function __destruct() { echo 'C;'; }
}
class BodyArrayReexit27Queue { function __destruct() { echo 'Q;'; } }
function body_array_reexit27_queue($arg) { echo 'BAD-QUEUE;'; }
function body_array_reexit27_final($bytes, $phase) {
    $callback = new BodyArrayReexit27Caller;
    $arg = new BodyArrayReexit27Arg;
    $later = new BodyArrayReexit27Later;
    $queue = new BodyArrayReexit27Queue;
    register_tick_function($callback, $arg, $later);
    register_shutdown_function('body_array_reexit27_queue', $queue);
    unset($callback, $arg, $later, $queue);
    return $bytes . 'F;';
}
ob_start('body_array_reexit27_final');
echo 'B;';
exit(263);
