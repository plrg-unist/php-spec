<?php
class FirstStackCaptureOB05 {
    public function __destruct() {
        $GLOBALS['stack_stage_ob05'] = 'first-entered';
        echo 'BAD-FIRST|';
    }
}
class SecondStackCaptureOB05 {
    public function __destruct() {
        $GLOBALS['stack_stage_ob05'] = 'second-entered';
        echo 'BAD-SECOND|';
    }
}
class StackObserverOB05 {
    public function __destruct() {
        echo 'A:', $GLOBALS['stack_stage_ob05'], '|';
    }
}
class StackFinalOB05 {
    public $after = null;
    public function __invoke(string $bytes, int $phase): string {
        $this->after = new StackObserverOB05;
        $GLOBALS['stack_stage_ob05'] = 'live';
        $firstCapture = new FirstStackCaptureOB05;
        $first = static function ($level, $message, $file, $line) use ($firstCapture) {
            echo 'BAD-ERROR-HANDLER|';
            return false;
        };
        $secondCapture = new SecondStackCaptureOB05;
        $second = static function ($level, $message, $file, $line) use ($secondCapture) {
            echo 'BAD-ERROR-HANDLER|';
            return false;
        };
        set_error_handler($first);
        set_error_handler($second);
        set_error_handler(null);
        return $bytes;
    }
}
ob_start(null, 0);
echo 'B|';
ob_start(new StackFinalOB05, 0);
echo 'T|';
