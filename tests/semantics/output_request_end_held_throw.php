<?php
function throwingFinalOB01(string $bytes, int $phase): string {
    global $exception;
    throw $exception;
}
$exception = new Exception('final-handler');
ob_start('throwingFinalOB01', 0);
echo 'T|';
