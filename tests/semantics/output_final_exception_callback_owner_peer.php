<?php
class CallbackTraceOwnerOB04 {
    public function __destruct() {
        $GLOBALS['original_stage'] = 'released';
        echo 'P|';
    }
}
class NoticeCaptureOwnerOB04 {
    public function __destruct() {
        $GLOBALS['notice_stage'] = 'released';
        echo 'C|';
    }
}
class CallbackRawObserverOB04 {
    public function __destruct() {
        echo 'A:', $GLOBALS['original_stage'], ':', $GLOBALS['notice_stage'], '|';
    }
}
function callbackOriginalOB04($payload) {
    return new Exception('callback-primary');
}
class CallbackFinalOwnerOB04 {
    public $after = null;
    public function __invoke(string $bytes, int $phase): string {
        $this->after = new CallbackRawObserverOB04;
        $GLOBALS['original_stage'] = 'live';
        $GLOBALS['notice_stage'] = 'live';
        $capture = new NoticeCaptureOwnerOB04;
        set_error_handler(static function ($level, $message, $file, $line) use ($capture) {
            echo 'D|';
            throw new Exception('callback-secondary');
        });
        throw callbackOriginalOB04(new CallbackTraceOwnerOB04);
    }
}
#[\Deprecated('before-callback-owner')]
function callbackSelectedOB04(Throwable $error) {
    echo 'BAD-BODY|';
}
set_exception_handler('callbackSelectedOB04');
ob_start(null, 0);
echo 'B|';
ob_start(new CallbackFinalOwnerOB04, 0);
echo 'T|';
