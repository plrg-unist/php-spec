<?php
class Operand365 {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/echo-cv-call-argument-warning-child.php'; }
    public function __destruct() {
        $e = new Exception('retire'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/echo-cv-call-argument-warning-child.php' ? 'child' : 'main'), '|';
        unset($GLOBALS['argument365']); echo 'UNSET|';
    }
}
function call365($value = 'DEFAULT') { echo 'CALL:', ($value === null ? 'NULL' : $value), '|'; return 'RESULT|'; }
set_error_handler(function ($severity, $message, $file, $line) { echo 'W:', $line, ':', $message, '|'; $GLOBALS['argument365'] = 'TOO-LATE'; return true; });
$argument365 = 'OLD';
$value = include new Operand365(); echo 'V:', $value, '|A:', $argument365, '|END';
