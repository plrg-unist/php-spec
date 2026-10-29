<?php
class LateFinalOB02 {
    public $exception = null;
    public function __destruct() {
        $fields = (array) $this->exception;
        if ($fields["\0Exception\0string"] === '') {
            echo 'U|';
        } else {
            echo 'C|';
        }
        echo 'L|';
    }
}
class LateOwnerOB02 {
    public $late = null;
    public function __invoke(string $bytes, int $phase): string {
        $this->late = new LateFinalOB02;
        $this->late->exception = new Exception('late-final');
        throw $this->late->exception;
    }
}
ob_start(null, 0);
echo 'B|';
ob_start(new LateOwnerOB02, 0);
echo 'T|';
