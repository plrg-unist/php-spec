<?php
class LocalFinalOB01 {
    public function __destruct() { echo 'D|'; }
}
function localFinalOB01(string $bytes, int $phase): string {
    $local = new LocalFinalOB01();
    return 'L|' . $phase . '|[' . $bytes . ']';
}
ob_start('localFinalOB01', 0);
echo 'x|';
