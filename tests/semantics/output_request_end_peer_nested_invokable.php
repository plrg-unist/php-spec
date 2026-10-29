<?php
class FinalInvokableOB01 {
    public function __invoke(string $bytes, int $phase): string {
        return '[H:' . $phase . ':' . ob_get_level() . ':' . $bytes . ']';
    }
    public function __destruct() { echo 'D|'; }
}
echo 'P|';
ob_start();
$handler = new FinalInvokableOB01();
ob_start($handler, 0);
$handler = null;
echo 'A|';
