<?php
class Operand361 {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/echo-call-result-warning-child.php'; }
    public function __destruct() {
        $e = new Exception('retire'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/echo-call-result-warning-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/echo-call-result-warning-child.php' ? 'filename' : 'none'), '|';
        echo 'RETIRE|';
    }
}
class Returned361 {
    public function __toString(): string { echo 'TEXT|'; return 'OBJECT|'; }
    public function __destruct() { echo 'RESULT-D|'; echo $missing361; echo 'RESULT-END|'; }
}
class Borrowed361 {
    public function __toString(): string { echo 'BORROW-TEXT|'; unset($GLOBALS['value361']); return 'BORROWED|'; }
    public function __destruct() { echo 'BORROW-D|'; }
}
function call361() { echo 'CALL|'; return new Returned361(); }
set_error_handler(function ($severity, $message, $file, $line) { echo 'W:', $line, ':', $message, '|'; return true; });
$value = include new Operand361(); echo 'V:', $value, '|END';
