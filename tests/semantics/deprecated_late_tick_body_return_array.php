<?php
class BodyArray22Child { function __destruct() { echo 'K;'; } }
class BodyArray22Value {
    public $owner;
    function __construct($owner) { $this->owner = $owner; }
    function __destruct() { echo 'R;'; }
}
class BodyArray22Arg {
    public $held;
    function __construct() { $this->held = new BodyArray22Child; }
    function __destruct() {
        echo 'A;';
        $returned = new BodyArray22Value($this);
        return [&$returned, $returned, $returned];
    }
}
class BodyArray22Later { function __destruct() { echo 'L;'; } }
class BodyArray22Caller {
    function __invoke(...$args) { echo 'BAD-CALL;'; }
    function __destruct() { echo 'C;'; }
}
function body_array22_final($bytes, $phase) {
    $callback = new BodyArray22Caller;
    $arg = new BodyArray22Arg;
    $later = new BodyArray22Later;
    register_tick_function($callback, $arg, $later);
    unset($callback, $arg, $later);
    return $bytes . 'F;';
}
ob_start('body_array22_final');
echo 'B;';
exit(263);
