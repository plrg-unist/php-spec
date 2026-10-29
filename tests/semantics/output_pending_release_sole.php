<?php
class BeforePendingOB03 {
    public function __destruct() { echo 'P|'; }
}
class AfterPendingOB03 {
    public function __destruct() { echo 'A|'; }
}
function makePendingOB03($payload) {
    return new Exception('pending-release');
}
class PendingHandlerOB03 {
    public $after = null;
    public $keep = null;
    public function __invoke(string $bytes, int $phase): string {
        $this->after = new AfterPendingOB03;
        throw makePendingOB03(new BeforePendingOB03);
    }
}
ob_start(null, 0);
echo 'B|';
ob_start(new PendingHandlerOB03, 0);
echo 'T|';
