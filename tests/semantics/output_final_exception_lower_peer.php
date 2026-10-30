<?php
class LowerTraceOwnerOB04 {
    public function __destruct() { echo 'P|'; }
}
class LowerRawObserverOB04 {
    public function __destruct() { echo 'A|'; }
}
function lowerOriginalOB04($payload) {
    return new Exception('handled-lower');
}
class LowerFinalOwnerOB04 {
    public $after = null;
    public function __invoke(string $bytes, int $phase): string {
        $this->after = new LowerRawObserverOB04;
        throw lowerOriginalOB04(new LowerTraceOwnerOB04);
    }
}
function handleLowerOB04(Throwable $error) {
    echo 'H:', get_exception_handler() === null, '|';
    return false;
}
function lowerBufferOB04(string $bytes, int $phase): string {
    return 'L[' . $bytes . ']';
}
set_exception_handler('handleLowerOB04');
ob_start('lowerBufferOB04', 0);
echo 'B|';
ob_start(new LowerFinalOwnerOB04, 0);
echo 'T|';
