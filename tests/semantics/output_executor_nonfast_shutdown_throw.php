<?php
class LateFccCaptureOB05 {
    public function __destruct() { echo 'BAD-FCC|'; }
}
class LateArgumentOB05 {
    public function __destruct() {
        echo 'Q|';
        throw new Exception('late-queue-secondary');
    }
}
class LateQueueFinalOB05 {
    public function __invoke($bytes, $phase) {
        $capture = new LateFccCaptureOB05;
        $callback = static function ($argument) use ($capture) {
            echo 'BAD-SHUTDOWN|';
        };
        register_shutdown_function($callback, new LateArgumentOB05);
        return false;
    }
}
ob_start(null, 0);
echo 'B|';
ob_start(new LateQueueFinalOB05, 0);
echo 'T|';
