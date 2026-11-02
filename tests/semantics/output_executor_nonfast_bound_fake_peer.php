<?php
class BoundFakeArgumentOB05 {
    public function __destruct() { echo 'A|'; }
}
class BoundFakeParentOB05 {
    public function pending($argument) { echo 'BAD-SHUTDOWN|'; }
}
class BoundFakeReceiverOB05 extends BoundFakeParentOB05 {
    public function __destruct() { echo 'R|'; }
}
class BoundFakeFinalOB05 {
    public function __invoke($bytes, $phase) {
        $original = new BoundFakeParentOB05;
        $callback = $original->pending(...);
        $receiver = new BoundFakeReceiverOB05;
        $bound = $callback->bindTo($receiver, BoundFakeParentOB05::class);
        register_shutdown_function($bound, new BoundFakeArgumentOB05);
        return false;
    }
}
ob_start(null, 0);
echo 'B|';
ob_start(new BoundFakeFinalOB05, 0);
echo 'T|';
