<?php
class CaptureOwnerOB04 {
    public function __destruct() { echo 'C|'; }
}
class ReturnedOwnerOB04 {
    public function __destruct() { echo 'R|'; }
}
class OriginalTraceOwnerOB04 {
    public function __destruct() { echo 'P|'; }
}
class RawObserverOB04 {
    public function __destruct() { echo 'A|'; }
}
function originalErrorOB04($payload) {
    return new Exception('handled-final');
}
class FinalOwnerOB04 {
    public $after = null;
    public function __invoke(string $bytes, int $phase): string {
        $this->after = new RawObserverOB04;
        $capture = new CaptureOwnerOB04;
        set_exception_handler(static function (Throwable $error) use ($capture) {
            echo 'H:', get_exception_handler() === null, '|';
            restore_exception_handler();
            restore_exception_handler();
            return new ReturnedOwnerOB04;
        });
        throw originalErrorOB04(new OriginalTraceOwnerOB04);
    }
}
ob_start(null, 0);
echo 'B|';
ob_start(new FinalOwnerOB04, 0);
echo 'T|';
