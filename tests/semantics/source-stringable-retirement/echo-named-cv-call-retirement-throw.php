<?php
class OperandEchoNamed {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/echo-named-cv-call-retirement-throw-child.php'; }
    public function __destruct() {
        $e = new Exception('retire'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/echo-named-cv-call-retirement-throw-child.php' ? 'child' : 'main'), '|';
        unset($GLOBALS['argumentEchoNamed']); echo 'UNSET|'; throw new RuntimeException('retire');
    }
}
set_error_handler(function ($severity, $message, $file, $line) { echo 'W:', $line, ':', $message, '|'; $GLOBALS['argumentEchoNamed'] = 'TOO-LATE'; return true; });
$argumentEchoNamed = 'OLD';
try { $value = include new OperandEchoNamed(); echo 'V:', $value, '|'; } catch (Throwable $e) { echo 'CATCH:', $e->getMessage(), ':', $e->getLine(), '|'; }
echo 'END';
