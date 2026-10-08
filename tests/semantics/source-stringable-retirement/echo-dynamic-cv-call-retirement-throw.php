<?php
class OperandEchoDynamic {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/echo-dynamic-cv-call-retirement-throw-child.php'; }
    public function __destruct() { $e = new Exception('retire'); $t = $e->getTrace(); echo 'D:', $t[0]['line'], '|'; unset($GLOBALS['calleeEchoDynamic']); throw new Exception('retire-stop'); }
}
set_error_handler(function ($level, $message, $file, $line) { echo 'WRONG-W:', $line, '|'; return true; });
try { include new OperandEchoDynamic(); } catch (Throwable $e) { echo 'CATCH:', $e->getMessage(), '|'; }
echo 'END';
