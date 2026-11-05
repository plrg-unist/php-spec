<?php
class BodyArrayExit26Child { function __destruct() { echo 'K;'; } }
class BodyArrayExit26Value {
    public $owner;
    function __construct($owner) { $this->owner = $owner; }
    function __destruct() { echo 'R;'; exit('E;'); echo 'BAD-R;'; }
}
class BodyArrayExit26Arg {
    public $held;
    function __construct() { $this->held = new BodyArrayExit26Child; }
    function __destruct() {
        echo 'A;';
        $returned = new BodyArrayExit26Value($this);
        return [&$returned, $returned, $returned];
    }
}
class BodyArrayExit26Later { function __destruct() { echo 'L;'; } }
class BodyArrayExit26Caller {
    function __invoke(...$args) { echo 'BAD-CALL;'; }
    function __destruct() { echo 'C;'; }
}
class BodyArrayExit26Queue { function __destruct() { echo 'Q;'; } }
function body_array_exit26_queue($arg) { echo 'BAD-QUEUE;'; }
function body_array_exit26_final($bytes, $phase) {
    $callback = new BodyArrayExit26Caller;
    $arg = new BodyArrayExit26Arg;
    $later = new BodyArrayExit26Later;
    $queue = new BodyArrayExit26Queue;
    register_tick_function($callback, $arg, $later);
    register_shutdown_function('body_array_exit26_queue', $queue);
    unset($callback, $arg, $later, $queue);
    return $bytes . 'F;';
}
ob_start('body_array_exit26_final');
echo 'B;';
exit(263);
