<?php
class WarningTraceOwnerOB04 {
    public function __destruct() { echo 'P|'; }
}
class WarningRawObserverOB04 {
    public function __destruct() { echo 'A|'; }
}
function warningOriginalOB04($payload) {
    return new Exception('warning-primary');
}
class WarningFinalOwnerOB04 {
    public $after = null;
    public function __invoke(string $bytes, int $phase): string {
        $this->after = new WarningRawObserverOB04;
        throw warningOriginalOB04(new WarningTraceOwnerOB04);
    }
}
#[\Deprecated('before-final-handler')]
function warningSelectedOB04(Throwable $error) {
    echo 'BAD-BODY|';
}
function warningNoticeOB04($level, $message, $file, $line) {
    echo 'D|';
    throw new Exception('pre-entry-secondary');
}
set_error_handler('warningNoticeOB04');
set_exception_handler('warningSelectedOB04');
ob_start(null, 0);
echo 'B|';
ob_start(new WarningFinalOwnerOB04, 0);
echo 'T|';
