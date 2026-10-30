<?php
class NormalLateCaptureOB04 {
    public function __destruct() {
        $GLOBALS['normal_capture_stage'] = 'released';
        echo 'C|';
    }
}
class NormalLateTraceOB04 {
    public function __destruct() { echo 'P|'; }
}
class NormalLateObserverOB04 {
    public function __destruct() {
        echo 'A:', $GLOBALS['normal_capture_stage'], '|';
    }
}
function normalLateErrorOB04($payload) {
    return new Exception('normal-late-primary');
}
class NormalLateFinalOB04 {
    public $after = null;
    public function __invoke(string $bytes, int $phase): string {
        $this->after = new NormalLateObserverOB04;
        throw normalLateErrorOB04(new NormalLateTraceOB04);
    }
}
function normalLateHandlerOB04(Throwable $error) {
    $capture = new NormalLateCaptureOB04;
    $GLOBALS['normal_capture_stage'] = 'live';
    set_error_handler(static function ($level, $message, $file, $line) use ($capture) {
        echo 'BAD-ERROR-HANDLER|';
        return false;
    });
    echo 'H|';
    return false;
}
set_exception_handler('normalLateHandlerOB04');
ob_start(null, 0);
echo 'B|';
ob_start(new NormalLateFinalOB04, 0);
echo 'T|';
