<?php
class ShutdownCaptureOB05 {
    public function __destruct() {
        $GLOBALS['shutdown_stage_ob05'] = 'released';
        echo 'C|';
    }
}
class ShutdownObserverOB05 {
    public function __destruct() {
        echo 'A:', $GLOBALS['shutdown_stage_ob05'], '|';
    }
}
class ShutdownFinalOB05 {
    public $after = null;
    public function __invoke(string $bytes, int $phase): string {
        $this->after = new ShutdownObserverOB05;
        $GLOBALS['shutdown_stage_ob05'] = 'live';
        $capture = new ShutdownCaptureOB05;
        register_shutdown_function(static function () use ($capture) {
            echo 'BAD-SHUTDOWN-CALL|';
        });
        return $bytes;
    }
}
ob_start(null, 0);
echo 'B|';
ob_start(new ShutdownFinalOB05, 0);
echo 'T|';
