<?php
class MethodFinalOB01 {
    public function filter(string $bytes, int $phase): string {
        return 'M|' . $phase . '|[' . $bytes . ']';
    }
    public function __destruct() { echo 'D|'; }
}
function shutdownFinalOB01(): void { echo 'S|'; }
register_shutdown_function('shutdownFinalOB01');
$handler = [new MethodFinalOB01(), 'filter'];
ob_start($handler, 0);
$handler = null;
echo 'E|';
