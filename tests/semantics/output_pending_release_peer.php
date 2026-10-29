<?php
class TraceOwnedOB03 {
    public function __destruct() {
        $GLOBALS['stage'] = 'released';
    }
}
class AfterZohOB03 {
    public function __destruct() {
        echo 'A:', $GLOBALS['stage'], '|';
    }
}
class FinalOwnerOB03 {
    public $after = null;
    public function __invoke(string $bytes, int $phase): string {
        $this->after = new AfterZohOB03;
        $GLOBALS['stage'] = 'pending';
        $error = makeFinalOB03(new TraceOwnedOB03);
        if ($GLOBALS['stage'] !== 'pending') {
            $GLOBALS['stage'] = 'released-before-throw';
        }
        throw $error;
    }
}
function makeFinalOB03(TraceOwnedOB03 $payload): Exception {
    return new Exception('trace-owned');
}
$GLOBALS['stage'] = 'setup';
ob_start(null, 0);
echo 'B|';
ob_start(new FinalOwnerOB03, 0);
echo 'T|';
