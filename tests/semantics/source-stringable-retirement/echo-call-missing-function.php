<?php
class Operand361 {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/echo-call-missing-function-child.php'; }
    public function __destruct() {
        $e = new Exception('retire'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/echo-call-missing-function-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/echo-call-missing-function-child.php' ? 'filename' : 'none'), '|';
        echo 'RETIRE|';
    }
}
try { include new Operand361(); } catch (Error $e) { echo 'CAUGHT:', $e->getMessage(), ':', $e->getLine(), '|'; } echo 'END';
