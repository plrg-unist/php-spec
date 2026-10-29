<?php
class TracePayloadOB04 {
    public function __destruct() { echo 'P|'; }
}
class RawChildOB04 {
    public function __destruct() { echo 'A|'; }
}
function makeFinalOB04($payload) {
    return new Exception('final-primary');
}
class OutputOwnerOB04 {
    public $after = null;
    public function __invoke(string $bytes, int $phase): string {
        $this->after = new RawChildOB04;
        throw makeFinalOB04(new TracePayloadOB04);
    }
}
function selectedFinalOB04($error) {
    echo 'H:', $error->getMessage(), '|';
    throw new Exception('handler-secondary');
}
set_exception_handler('selectedFinalOB04');
ob_start(null, 0);
echo 'B|';
ob_start(new OutputOwnerOB04, 0);
echo 'T|';
