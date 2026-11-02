<?php
class BoundFccArgumentOB05 {
    public function __destruct() { echo 'A|'; }
}
class BoundFccCaptureOB05 {
    public function __destruct() { echo 'C|'; }
}
class BoundFccReceiverOB05 {
    public function __destruct() { echo 'R|'; }
    public function make($capture) {
        return function ($argument) use ($capture) {
            echo 'BAD-SHUTDOWN|';
        };
    }
}
class BoundFccFinalOB05 {
    public function __invoke($bytes, $phase) {
        $receiver = new BoundFccReceiverOB05;
        $capture = new BoundFccCaptureOB05;
        $callback = $receiver->make($capture);
        register_shutdown_function($callback, new BoundFccArgumentOB05);
        return false;
    }
}
ob_start(null, 0);
echo 'B|';
ob_start(new BoundFccFinalOB05, 0);
echo 'T|';
