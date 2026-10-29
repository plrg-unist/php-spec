<?php
$exception = new Exception('supplied-final');
$handler = function (string $bytes, int $phase) use ($exception): string {
    throw $exception;
};
ob_start($handler, 0);
$handler = null;
$exception = null;
echo 'T|';
